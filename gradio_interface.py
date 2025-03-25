"""
Gradio Interface for Steam Games Downloader
"""

import os
import logging
import gradio as gr
from download_manager import get_download_manager
from library_manager import get_library_manager
from config import get_config

logger = logging.getLogger(__name__)

class SteamDownloaderInterface:
    def __init__(self):
        self.download_mgr = get_download_manager()
        self.library_mgr = get_library_manager()
        self.config = get_config()
        self.download_mgr.start_worker()

    def create_interface(self):
        """Create the main Gradio interface"""
        with gr.Blocks(
            title="Steam Games Downloader",
            theme=gr.themes.Soft(),
            css=self._get_css()
        ) as interface:
            # Header
            gr.Markdown("# Steam Games Downloader")
            
            # Access info section
            with gr.Row(elem_classes="access-info-container"):
                with gr.Column():
                    gr.Markdown("### Access Information")
                    
                    # Check if tunneling binary exists
                    tunneling_available = os.path.exists("/usr/local/lib/python3.10/site-packages/gradio/frpc_linux_amd64_v0.3")
                    if tunneling_available:
                        gr.Markdown("✅ **Public sharing is available** - A public URL will be generated when the app starts.")
                    else:
                        gr.Markdown("⚠️ **Public sharing is NOT available** - This app can only be accessed via direct URL.")
                        gr.Markdown("To access this application, use one of these methods:")
                        gr.Markdown("1. Access via the container's hostname/IP and port")
                        gr.Markdown("2. Set up a reverse proxy or ingress to expose this service")
                        gr.Markdown("3. Configure port forwarding if running locally")
            
            # Tabbed interface
            with gr.Tabs():
                with gr.Tab("Download"):
                    self._create_download_tab()
                
                with gr.Tab("Library"):
                    self._create_library_tab()
                
                with gr.Tab("Settings"):
                    self._create_settings_tab()
            
            # Footer
            gr.Markdown("---")
            gr.Markdown("> Steam Games Downloader | Running in container mode")

        return interface
    
    def _create_download_tab(self):
        """Download game tab UI"""
        with gr.Row():
            with gr.Column(scale=2):
                game_id = gr.Textbox(label="Steam App ID")
                game_name = gr.Textbox(label="Game Name")
                download_btn = gr.Button("Start Download")
            
            with gr.Column(scale=3):
                status = gr.Textbox(label="Download Status", interactive=False)
                progress = gr.Progress()
                
        download_btn.click(
            fn=self._start_download,
            inputs=[game_id, game_name],
            outputs=[status]
        )

    def _create_library_tab(self):
        """Game library tab UI"""
        with gr.Row():
            library_df = self.library_mgr.get_library_dataframe()
            gr.Dataframe(
                value=library_df,
                headers=["App ID", "Name", "Location", "Size", "Last Played"],
                interactive=False
            )

    def _create_settings_tab(self):
        """Settings tab UI"""
        with gr.Row():
            with gr.Column():
                gr.Markdown("### SteamCMD Settings")
                steamcmd_path = gr.Textbox(
                    label="SteamCMD Path",
                    value=self.config.get("steamcmd_path")
                )
                test_btn = gr.Button("Test SteamCMD")
                test_output = gr.Textbox(label="Test Result")
                
                test_btn.click(
                    fn=self._test_steamcmd,
                    inputs=[steamcmd_path],
                    outputs=[test_output]
                )

    def _start_download(self, app_id, game_name):
        """Start a download and return status"""
        try:
            if not app_id or not game_name:
                return "Error: App ID and Game Name required"
            
            # Validate inputs
            try:
                app_id = int(app_id.strip())
            except ValueError:
                return "Error: App ID must be a number"
                
            game_name = game_name.strip()
            if not game_name:
                return "Error: Game Name cannot be empty"
            
            # Add to download queue with error handling
            try:
                download_id = self.download_mgr.add_download(app_id, game_name)
                return f"Download queued (ID: {download_id})"
            except Exception as e:
                logger.error(f"Error adding download: {str(e)}")
                return f"Error starting download: {str(e)}"
                
        except Exception as e:
            logger.error(f"Unexpected error in start download: {str(e)}")
            return f"An unexpected error occurred: {str(e)}"

    def _test_steamcmd(self, path):
        """Test SteamCMD installation"""
        from steamcmd_manager import get_steamcmd
        try:
            steamcmd = get_steamcmd()
            if steamcmd.run_command(["+quit"]):
                return "✅ SteamCMD working correctly"
            return "❌ SteamCMD test failed"
        except Exception as e:
            return f"Error: {str(e)}"

    def _get_css(self):
        """Return custom CSS styles"""
        return """
        .status-pending { color: #6c757d; }
        .status-downloading { color: #007bff; font-weight: bold; }
        .status-completed { color: #28a745; font-weight: bold; }
        .status-failed { color: #dc3545; font-weight: bold; }
        .container { margin: 0.5em 0; }
        .access-info-container { 
            border: 1px solid #ddd; 
            border-radius: 8px; 
            padding: 10px; 
            margin-bottom: 20px;
            background-color: #f8f9fa;
        }
        """

def create_interface():
    """Create and return the Gradio interface"""
    return SteamDownloaderInterface().create_interface()

if __name__ == "__main__":
    # For testing
    logging.basicConfig(level=logging.INFO)
    interface = create_interface()
    interface.launch()