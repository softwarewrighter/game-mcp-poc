use axum::{
    Router,
    extract::State,
    http::StatusCode,
    response::{IntoResponse, Json, Response},
    routing::{get, post},
};
use serde_json::json;
use shared::{GameError, GameState, MakeMoveRequest, TauntRequest};
use std::sync::{Arc, Mutex};
use tracing::info;

use crate::game::manager::GameManager;

/// Shared application state
#[derive(Clone)]
pub struct AppState {
    pub game_manager: Arc<Mutex<GameManager>>,
}

/// Wrapper for GameError to implement IntoResponse
struct ApiError(GameError);

impl From<GameError> for ApiError {
    fn from(err: GameError) -> Self {
        ApiError(err)
    }
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let (status, message) = match self.0 {
            GameError::CellOccupied { .. }
            | GameError::OutOfBounds { .. }
            | GameError::WrongTurn { .. }
            | GameError::GameOver { .. } => (StatusCode::BAD_REQUEST, self.0.to_string()),
            GameError::GameNotFound => (StatusCode::NOT_FOUND, self.0.to_string()),
            GameError::DatabaseError { .. } | GameError::InternalError { .. } => {
                (StatusCode::INTERNAL_SERVER_ERROR, self.0.to_string())
            }
        };

        (status, Json(json!({ "error": message }))).into_response()
    }
}

/// GET /api/game - Get current game state
async fn get_game_state(State(state): State<AppState>) -> Result<Json<GameState>, ApiError> {
    info!("GET /api/game");

    let mut manager = state.game_manager.lock().unwrap();
    let game_state = manager.get_or_create_game()?;

    info!("Returning game state: {}", game_state.id);
    Ok(Json(game_state))
}

/// POST /api/game/new - Create a new game
async fn create_new_game(State(state): State<AppState>) -> Result<Json<GameState>, ApiError> {
    info!("POST /api/game/new");

    let mut manager = state.game_manager.lock().unwrap();
    let game_state = manager.restart_game()?;

    info!("Created new game: {}", game_state.id);
    Ok(Json(game_state))
}

/// POST /api/game/move - Make a move
async fn make_move(
    State(state): State<AppState>,
    Json(request): Json<MakeMoveRequest>,
) -> Result<Json<GameState>, ApiError> {
    info!(
        "POST /api/game/move - row: {}, col: {}",
        request.row, request.col
    );

    let mut manager = state.game_manager.lock().unwrap();
    let game_state = manager.make_move(request.row, request.col)?;

    info!("Move made successfully");
    Ok(Json(game_state))
}

/// POST /api/game/taunt - Add a taunt message
async fn add_taunt(
    State(state): State<AppState>,
    Json(request): Json<TauntRequest>,
) -> Result<StatusCode, ApiError> {
    info!("POST /api/game/taunt - message: {}", request.message);

    let mut manager = state.game_manager.lock().unwrap();
    manager.add_taunt(request.message)?;

    info!("Taunt added successfully");
    Ok(StatusCode::OK)
}

/// Health check endpoint
async fn health_check() -> &'static str {
    "OK"
}

/// Create the API router
pub fn create_router(state: AppState) -> Router {
    Router::new()
        .route("/health", get(health_check))
        .route("/api/game", get(get_game_state))
        .route("/api/game/new", post(create_new_game))
        .route("/api/game/move", post(make_move))
        .route("/api/game/taunt", post(add_taunt))
        .with_state(state)
}

// Unit tests removed - see api_integration.rs for comprehensive API tests via actual HTTP requests
