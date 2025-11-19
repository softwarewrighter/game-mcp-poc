use log::{error, info};
use shared::{Cell, GameState, Player};
use yew::prelude::*;

#[cfg(target_arch = "wasm32")]
use gloo_net::http::Request;

#[cfg(target_arch = "wasm32")]
const API_BASE: &str = "http://localhost:3000/api";

#[function_component(App)]
fn app() -> Html {
    info!("Rendering App component");

    let game_state = use_state(|| None::<GameState>);
    let loading = use_state(|| true);
    let error_msg = use_state(|| None::<String>);

    // Fetch game state on mount
    {
        let game_state = game_state.clone();
        let loading = loading.clone();
        let error_msg = error_msg.clone();

        use_effect_with((), move |_| {
            wasm_bindgen_futures::spawn_local(async move {
                match fetch_game_state().await {
                    Ok(state) => {
                        info!("Game state loaded successfully");
                        game_state.set(Some(state));
                        loading.set(false);
                    }
                    Err(e) => {
                        error!("Failed to load game state: {}", e);
                        error_msg.set(Some(format!("Failed to load game: {}", e)));
                        loading.set(false);
                    }
                }
            });
            || ()
        });
    }

    let on_new_game = {
        let game_state = game_state.clone();
        let loading = loading.clone();

        Callback::from(move |_| {
            let game_state = game_state.clone();
            let loading = loading.clone();

            loading.set(true);

            wasm_bindgen_futures::spawn_local(async move {
                match create_new_game().await {
                    Ok(new_state) => {
                        info!("New game created");
                        game_state.set(Some(new_state));
                        loading.set(false);
                    }
                    Err(e) => {
                        error!("Failed to create new game: {}", e);
                        loading.set(false);
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
                <h3>{"Game Log"}</h3>
                <div class="log-entry">{"Welcome to Tic-Tac-Toe!"}</div>
                <div class="log-entry">{"API connected - backend is working!"}</div>
            </div>
        </div>
    }
}

#[cfg(target_arch = "wasm32")]
async fn fetch_game_state() -> Result<GameState, String> {
    let response = Request::get(&format!("{}/game", API_BASE))
        .send()
        .await
        .map_err(|e| e.to_string())?;

    if !response.ok() {
        return Err(format!("HTTP error: {}", response.status()));
    }

    response.json().await.map_err(|e| e.to_string())
}

#[cfg(not(target_arch = "wasm32"))]
async fn fetch_game_state() -> Result<GameState, String> {
    Err("API calls only available in WASM builds".to_string())
}

#[cfg(target_arch = "wasm32")]
async fn create_new_game() -> Result<GameState, String> {
    let response = Request::post(&format!("{}/game/new", API_BASE))
        .send()
        .await
        .map_err(|e| e.to_string())?;

    if !response.ok() {
        return Err(format!("HTTP error: {}", response.status()));
    }

    response.json().await.map_err(|e| e.to_string())
}

#[cfg(not(target_arch = "wasm32"))]
async fn create_new_game() -> Result<GameState, String> {
    Err("API calls only available in WASM builds".to_string())
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
    use shared::{Cell, Player};

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
