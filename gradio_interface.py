"""
Gradio Interface for Steam Games Downloader
"""

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
                progress = gr.ProgressBar()
                
        download_btn.click(
            fn=self._start_download,
            inputs=[game_id, game_name],
            outputs=[status, progress]
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
        if not app_id or not game_name:
            return "Error: App ID and Game Name required", 0
        
        download_id = self.download_mgr.add_download(app_id, game_name)
        return f"Download queued (ID: {download_id})", 0.1

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
        """

def create_interface():
    """Create and return the Gradio interface"""
    return SteamDownloaderInterface().create_interface()

if __name__ == "__main__":
    # For testing
    logging.basicConfig(level=logging.INFO)
    interface = create_interface()
    interface.launch()