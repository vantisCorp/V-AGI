"""
OMNI-AI Main Application Entry Point
"""

import asyncio
import sys
from pathlib import Path
from loguru import logger

from config import settings


def setup_logging():
    """Configure logging for the application."""
    log_dir = Path(settings.log_file_path).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.remove()  # Remove default handler
    
    # Console logging
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # File logging
    logger.add(
        settings.log_file_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=settings.log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )


async def main():
    """Main application entry point."""
    setup_logging()
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    
    try:
        # Import and initialize core components
        from nexus.orchestrator import NexusOrchestrator
        from security.aegis import AegisGuardian
        from memory.working_memory import WorkingMemory
        from memory.long_term_memory import LongTermMemory
        
        logger.info("Initializing core components...")
        
        # Initialize security layer
        aegis = AegisGuardian()
        logger.info("AEGIS Guardian Layer initialized")
        
        # Initialize memory systems
        working_memory = WorkingMemory(max_size=settings.working_memory_size)
        long_term_memory = LongTermMemory(enabled=settings.long_term_memory_enabled)
        logger.info("Memory systems initialized")
        
        # Initialize NEXUS orchestrator
        nexus = NexusOrchestrator(
            max_concurrent_agents=settings.max_concurrent_agents,
            working_memory=working_memory,
            long_term_memory=long_term_memory
        )
        logger.info("NEXUS Orchestrator initialized")
        
        # Start the orchestrator
        await nexus.start()
        
        logger.success("OMNI-AI system started successfully!")
        logger.info("System is ready to process tasks")
        
        # Keep the application running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        await nexus.stop()
        logger.success("OMNI-AI system stopped successfully")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())