use super::routes::{AppState, create_router};
use crate::game::manager::GameManager;
use axum::Router;
use std::sync::{Arc, Mutex};
use tower_http::cors::{Any, CorsLayer};
use tower_http::services::ServeDir;
use tracing::info;

/// Start the HTTP server
pub async fn start_server(db_path: &str, port: u16) -> Result<(), Box<dyn std::error::Error>> {
    info!("Starting HTTP server on port {}", port);
    info!("Database path: {}", db_path);

    // Create game manager
    let manager =
        GameManager::new(db_path).map_err(|e| format!("Failed to create game manager: {}", e))?;

    let state = AppState {
        game_manager: Arc::new(Mutex::new(manager)),
    };

    // Create CORS layer to allow frontend access
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    // Create API router
    let api_router = create_router(state);

    // Combine API routes with static file serving
    let app = Router::new()
        .merge(api_router)
        .nest_service("/", ServeDir::new("frontend/dist"))
        .layer(cors);

    // Start server
    let addr = format!("0.0.0.0:{}", port);
    let listener = tokio::net::TcpListener::bind(&addr).await?;

    info!("Server listening on http://{}", addr);
    info!("API available at http://{}:{}/api/game", "localhost", port);
    info!("Frontend available at http://{}:{}/", "localhost", port);

    axum::serve(listener, app).await?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_server_can_be_created() {
        // Just verify the server setup doesn't panic
        let _manager = GameManager::new(":memory:").expect("Failed to create manager");
    }
}
