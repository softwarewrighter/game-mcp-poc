mod api;

use log::info;

#[cfg(target_arch = "wasm32")]
use log::error;
use shared::{Cell, GameState, Player};
use yew::prelude::*;

#[cfg(target_arch = "wasm32")]
use web_sys::EventSource;

#[cfg(target_arch = "wasm32")]
use wasm_bindgen::JsCast;

#[cfg(target_arch = "wasm32")]
use wasm_bindgen::closure::Closure;

#[function_component(App)]
fn app() -> Html {
    info!("Rendering App component");

    let game_state = use_state(|| None::<GameState>);
    let loading = use_state(|| true);
    let error_msg = use_state(|| None::<String>);
    let event_log = use_state(|| {
        vec![
            "Welcome to Tic-Tac-Toe!".to_string(),
            "Initializing...".to_string(),
        ]
    });

    // Log an event
    let log_event = {
        let event_log = event_log.clone();
        Callback::from(move |msg: String| {
            let mut logs = (*event_log).clone();
            logs.push(msg);
            // Keep only last 10 events
            if logs.len() > 10 {
                logs.remove(0);
            }
            event_log.set(logs);
        })
    };

    // Fetch initial state and set up SSE connection
    {
        #[cfg(target_arch = "wasm32")]
        let game_state = game_state.clone();
        #[cfg(target_arch = "wasm32")]
        let loading = loading.clone();
        #[cfg(target_arch = "wasm32")]
        let error_msg = error_msg.clone();
        let log_event = log_event.clone();

        use_effect_with((), move |_| {
            info!("Setting up SSE connection");
            log_event.emit("📡 Connecting to server via SSE...".to_string());

            // Initial fetch
            #[cfg(target_arch = "wasm32")]
            wasm_bindgen_futures::spawn_local({
                let game_state = game_state.clone();
                let loading = loading.clone();
                let error_msg = error_msg.clone();
                let log_event = log_event.clone();

                async move {
                    match api::fetch_game_state().await {
                        Ok(state) => {
                            game_state.set(Some(state));
                            loading.set(false);
                            error_msg.set(None);
                            log_event.emit("✅ Initial game state loaded".to_string());
                        }
                        Err(e) => {
                            error!("Failed to load initial game state: {}", e);
                            error_msg.set(Some(format!("API Error: {}", e)));
                            loading.set(false);
                            log_event.emit(format!("⚠️ Failed to load game: {}", e));
                        }
                    }
                }
            });

            // Set up SSE connection
            #[cfg(target_arch = "wasm32")]
            let event_source_opt = EventSource::new("http://localhost:3000/api/events").ok();

            #[cfg(target_arch = "wasm32")]
            if let Some(ref event_source) = event_source_opt {
                log_event.emit("✅ SSE connected - listening for updates".to_string());

                // Handle incoming messages
                let onmessage = Closure::wrap(Box::new(move |event: web_sys::MessageEvent| {
                    if let Some(data) = event.data().as_string() {
                        info!("SSE message received: {}", data);
                        match serde_json::from_str::<GameState>(&data) {
                            Ok(new_state) => {
                                game_state.set(Some(new_state));
                            }
                            Err(e) => {
                                error!("Failed to parse SSE data: {}", e);
                            }
                        }
                    }
                }) as Box<dyn FnMut(_)>);

                event_source.set_onmessage(Some(onmessage.as_ref().unchecked_ref()));
                onmessage.forget(); // Keep closure alive

                // Handle errors
                let onerror = Closure::wrap(Box::new(move |e: web_sys::Event| {
                    error!("SSE error: {:?}", e);
                    log_event.emit("⚠️ SSE connection error".to_string());
                }) as Box<dyn FnMut(_)>);

                event_source.set_onerror(Some(onerror.as_ref().unchecked_ref()));
                onerror.forget();
            } else {
                #[cfg(target_arch = "wasm32")]
                {
                    error!("Failed to create EventSource");
                    log_event.emit("❌ Failed to connect to SSE".to_string());
                }
            }

            // Cleanup function
            move || {
                #[cfg(target_arch = "wasm32")]
                if let Some(es) = event_source_opt {
                    es.close();
                }
            }
        });
    }

    // Track move count to detect changes
    let prev_move_count = use_state(|| 0);
    {
        let prev_move_count = prev_move_count.clone();
        let log_event = log_event.clone();
        let game_state = game_state.clone();

        use_effect_with(game_state.clone(), move |state| {
            if let Some(state) = state.as_ref() {
                let current_count = state.move_history.len();
                if current_count > *prev_move_count {
                    let last_move = &state.move_history[current_count - 1];
                    log_event.emit(format!(
                        "🎮 {} moved to ({}, {})",
                        last_move.player, last_move.row, last_move.col
                    ));
                    prev_move_count.set(current_count);
                }
            }
            || ()
        });
    }

    let on_new_game = {
        #[cfg(target_arch = "wasm32")]
        let game_state = game_state.clone();
        let loading = loading.clone();
        let log_event = log_event.clone();

        Callback::from(move |_| {
            #[cfg(target_arch = "wasm32")]
            let game_state = game_state.clone();
            let loading = loading.clone();
            let log_event = log_event.clone();

            loading.set(true);
            log_event.emit("🔄 Creating new game...".to_string());

            #[cfg(target_arch = "wasm32")]
            wasm_bindgen_futures::spawn_local(async move {
                match api::create_new_game().await {
                    Ok(new_state) => {
                        info!("New game created");
                        game_state.set(Some(new_state));
                        loading.set(false);
                        log_event.emit("✨ New game started!".to_string());
                    }
                    Err(e) => {
                        error!("Failed to create new game: {}", e);
                        loading.set(false);
                        log_event.emit(format!("❌ Failed to create game: {}", e));
                    }
                }
            });
        })
    };

    let game_info = if *loading {
        html! { <p>{"Game is loading..."}</p> }
    } else if let Some(ref err) = *error_msg {
        html! { <p class="error">{err}</p> }
    } else if let Some(ref state) = *game_state {
        let status_text = match &state.status {
            shared::GameStatus::InProgress => {
                format!("{}'s turn", state.current_turn)
            }
            shared::GameStatus::Won(player) => format!("{} wins!", player),
            shared::GameStatus::Draw => "It's a draw!".to_string(),
        };
        html! { <p>{format!("You are {}. {}", state.human_player, status_text)}</p> }
    } else {
        html! { <p>{"Click 'New Game' to start"}</p> }
    };

    let board_cells = if let Some(ref state) = *game_state {
        (0..9)
            .map(|i| {
                let row = i / 3;
                let col = i % 3;
                let cell = state.board[row][col];
                let cell_text = match cell {
                    Cell::Empty => "",
                    Cell::Occupied(Player::X) => "X",
                    Cell::Occupied(Player::O) => "O",
                };

                html! {
                    <div class="cell" key={i}>
                        {cell_text}
                    </div>
                }
            })
            .collect::<Html>()
    } else {
        (0..9)
            .map(|i| {
                html! {
                    <div class="cell" key={i}>
                        {""}
                    </div>
                }
            })
            .collect::<Html>()
    };

    // Render event log
    let log_entries = (*event_log)
        .iter()
        .rev()
        .map(|entry| {
            html! { <div class="log-entry">{entry}</div> }
        })
        .collect::<Html>();

    html! {
        <div class="app-container">
            <h1>{"Tic-Tac-Toe MCP Game"}</h1>
            <div class="game-info">
                {game_info}
            </div>
            <div class="game-board">
                {board_cells}
            </div>
            <div class="controls">
                <button class="btn-primary" onclick={on_new_game} disabled={*loading}>
                    {"New Game"}
                </button>
            </div>
            <div class="log-container">
                <h3>{"Event Log"}</h3>
                <div class="log-scroll">
                    {log_entries}
                </div>
            </div>
        </div>
    }
}

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen::prelude::wasm_bindgen(start)]
pub fn main() {
    // Initialize logging
    console_log::init_with_level(log::Level::Debug).expect("Failed to initialize logger");
    info!("Starting Tic-Tac-Toe frontend");

    yew::Renderer::<App>::new().render();
}

#[cfg(not(target_arch = "wasm32"))]
pub fn main() {
    println!("This application is designed to run in the browser with WASM");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_player_types_used_in_component() {
        // Validate that Player enum used in the game component works correctly
        let player_x = Player::X;
        let player_o = Player::O;
        assert_ne!(player_x, player_o);
        assert_eq!(player_x.opponent(), player_o);
        assert_eq!(player_o.opponent(), player_x);
    }

    #[test]
    fn test_cell_types_used_in_board() {
        // Validate that Cell enum used to render the board works correctly
        let empty = Cell::Empty;
        let occupied_x = Cell::Occupied(Player::X);
        let occupied_o = Cell::Occupied(Player::O);

        assert_eq!(empty, Cell::default());
        assert_ne!(empty, occupied_x);
        assert_ne!(occupied_x, occupied_o);
    }
}
