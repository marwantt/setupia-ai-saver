import os
import asyncio
import tempfile
import json
import subprocess
import shutil
import logging
import re
from pathlib import Path
from typing import Optional, List

from telegram import Update, Document, Video, PhotoSize, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode
import aiofiles
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables
load_dotenv()

# Reddit API configuration
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET") 
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "SetupiaAISaver/1.0")

# Instagram configuration
INSTAGRAM_COOKIES_FILE = os.getenv("INSTAGRAM_COOKIES_FILE")

class SetupiaAISaver:
    def __init__(self, token: str):
        self.token = token
        self.app = Application.builder().token(token).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Setup bot command and message handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_url))
        self.app.add_handler(CallbackQueryHandler(self.quality_callback))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        logging.info(f"Start command received from user: {user.first_name} (@{user.username})")

        welcome_message = """🤖 **Setupia AI Saver**

✅ **Bot is ready!**

Just send me any URL and I'll download it for you!"""

        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
        logging.info(f"Welcome message sent successfully to {user.first_name}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📋 **Setupia AI Saver - Social Media Focused**

📱 **Social Media Platforms:**
• **Instagram**: Posts, reels, stories, IGTV
• **Twitter/X**: Videos, images, threads
• **TikTok**: Videos, shorts
• **Facebook**: Videos, photos, posts
• **Pinterest**: Pins, boards, collections
• **Reddit**: Posts, images, videos
• **Tumblr**: Posts, images, GIFs

🎨 **Creative Platforms:**
• **DeviantArt**: Artwork, galleries
• **Behance**: Portfolio projects
• **Flickr**: Photos, albums

📺 **Video Platforms:**
• **YouTube**: All qualities (144p-4K)
• **Vimeo, Dailymotion, SoundCloud**
• **1000+ more platforms**

**Usage:**
1. Send me any URL from supported platforms
2. I'll process and download the media
3. Receive your files with formatted descriptions

**Examples:**
• `https://instagram.com/p/ABC123/`
• `https://pinterest.com/pin/12345/`
• `https://twitter.com/user/status/12345`
• `https://reddit.com/r/pics/comments/abc/`

Just paste the link and I'll handle the rest! 🚀
        """
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)

    async def handle_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle URL messages and download media"""
        url = update.message.text.strip()
        
        # Clean up URL format
        if url.startswith('@'):
            url = url[1:]  # Remove @ symbol
        
        # Remove tracking parameters that can cause issues
        tracking_params = ['utm_source=', 'utm_medium=', 'utm_name=', 'utm_term=', 'utm_content=', 'utm_campaign=']
        for param in tracking_params:
            if f'?{param}' in url:
                url = url.split(f'?{param}')[0]
                break
            elif f'&{param}' in url:
                url = url.split(f'&{param}')[0]
                break
        user = update.effective_user

        logging.info(f"URL received from {user.first_name}: {url}")

        if not self.is_valid_url(url):
            await update.message.reply_text("❌ Please send a valid URL from supported platforms.")
            return

        # Send processing message
        processing_msg = await update.message.reply_text("🔄 Processing your request...")
        logging.info(f"Starting download process for: {url}")

        # Create a temporary directory that we control
        temp_dir = tempfile.mkdtemp(prefix="setupia_")

        try:
            # Check if it's YouTube - show quality options
            if self.is_youtube_url(url):
                await processing_msg.edit_text("🔍 Getting available quality options...")
                formats = await self.get_youtube_formats(url)

                if formats:
                    keyboard = []

                    # Create quality buttons
                    for fmt in formats:
                        if fmt['quality'] == 'Audio Only':
                            quality_text = f"🎵 {fmt['quality']} (M4A)"
                        else:
                            quality_text = f"📺 {fmt['quality']} (Video Only)"
                        callback_data = f"quality:{fmt['id']}:{url}"
                        keyboard.append([InlineKeyboardButton(quality_text, callback_data=callback_data)])

                    # Add best quality auto-select option
                    keyboard.append([InlineKeyboardButton("⭐ Best Available", callback_data=f"quality:best:{url}")])

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    quality_message = f"""```
Available formats:
{chr(10).join([f"• {fmt['quality']}" for fmt in formats])}
```"""

                    await processing_msg.edit_text(
                        quality_message,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.MARKDOWN
                    )

                    # Store URL for callback
                    context.user_data['pending_url'] = url
                    context.user_data['temp_dir'] = temp_dir
                    return

                else:
                    # Fallback if can't get formats
                    await processing_msg.edit_text("🔄 Getting formats failed, downloading best quality...")
                    media_info = await self.download_with_yt_dlp(url, temp_dir)
            else:
                # Detect platform and choose optimal downloader
                platform = self.is_social_media_url(url)
                
                # Platform-specific download strategy
                if platform == 'instagram':
                    # Analyze Instagram content first to determine best tool
                    await processing_msg.edit_text("🔍 Analyzing Instagram content...")
                    analysis = await self.analyze_instagram_content(url)
                    
                    if analysis['type'] == 'auth_required':
                        if not INSTAGRAM_COOKIES_FILE or not Path(INSTAGRAM_COOKIES_FILE).exists():
                            await processing_msg.edit_text("🔐 Instagram content requires authentication.\n\n💡 **Permission Request:**\nTo download Instagram stories/posts, I need your browser cookies (login session).\n\n📋 **Setup steps:**\n1. Install 'Get cookies.txt LOCALLY' Chrome extension\n2. Login to Instagram\n3. Export cookies to cookies/instagram_cookies.txt\n\n🔒 **Privacy:** Cookies stay on your device only.\n\n📖 See GET_INSTAGRAM_COOKIES.md for detailed guide.")
                            return
                        else:
                            # Try with cookies
                            await processing_msg.edit_text("🔐 Using your Instagram cookies for authentication...")
                            analysis['best_tool'] = 'gallery-dl'  # Use gallery-dl with cookies
                    
                    # Use the best tool based on analysis
                    if analysis.get('type') == 'video':
                        await processing_msg.edit_text(f"🎬 Instagram video detected, using yt-dlp...")
                        media_info = await self.download_with_yt_dlp(url, temp_dir)
                        if not media_info:
                            await processing_msg.edit_text("🔄 Trying gallery-dl for video...")
                            media_info = await self.download_with_gallery_dl(url, temp_dir)
                    elif analysis.get('type') == 'image':
                        await processing_msg.edit_text(f"📸 Instagram image detected, using gallery-dl...")
                        media_info = await self.download_with_gallery_dl(url, temp_dir)
                        if not media_info:
                            await processing_msg.edit_text("🔄 Trying yt-dlp for image...")
                            media_info = await self.download_with_yt_dlp(url, temp_dir)
                    else:
                        # Unknown or mixed content - use gallery-dl first (Instagram default)
                        await processing_msg.edit_text(f"📱 Instagram content detected, using gallery-dl...")
                        media_info = await self.download_with_gallery_dl(url, temp_dir)
                        if not media_info:
                            await processing_msg.edit_text("🔄 Trying yt-dlp as fallback...")
                            media_info = await self.download_with_yt_dlp(url, temp_dir)
                            
                elif platform in ['pinterest', 'deviantart', 'flickr', 'behance', 'tumblr']:
                    # Image-focused platforms: gallery-dl first
                    await processing_msg.edit_text(f"🎨 Downloading from {platform.title()}...")
                    media_info = await self.download_with_gallery_dl(url, temp_dir)
                    
                    if not media_info:
                        await processing_msg.edit_text(f"🔄 Trying alternative method for {platform.title()}...")
                        media_info = await self.download_with_yt_dlp(url, temp_dir)
                        
                elif platform in ['facebook', 'reddit', 'linkedin']:
                    # Video-focused platforms: yt-dlp first
                    await processing_msg.edit_text(f"📺 Downloading from {platform.title()}...")
                    media_info = await self.download_with_yt_dlp(url, temp_dir)
                    
                    if not media_info:
                        await processing_msg.edit_text(f"🔄 Trying alternative method for {platform.title()}...")
                        media_info = await self.download_with_gallery_dl(url, temp_dir)
                        
                elif platform in ['twitter', 'telegram']:
                    # Mixed content platforms: balanced approach
                    await processing_msg.edit_text(f"📱 Downloading from {platform.title()}...")
                    media_info = await self.download_with_gallery_dl(url, temp_dir)
                    
                    if not media_info:
                        media_info = await self.download_with_yt_dlp(url, temp_dir)
                        
                else:
                    # Unknown/other platforms: try both methods
                    await processing_msg.edit_text("🔍 Detecting platform and downloading...")
                    media_info = await self.download_with_gallery_dl(url, temp_dir)
                    
                    if not media_info:
                        media_info = await self.download_with_yt_dlp(url, temp_dir)

            if 'media_info' in locals() and media_info:
                await self.send_media_to_user(update, media_info)
                await processing_msg.delete()
            elif not self.is_youtube_url(url):
                await processing_msg.edit_text("❌ Download failed or timed out. This can happen with:\n• Very long videos\n• Private content\n• Unsupported formats\n\nTry a shorter video or different URL!")

        except Exception as e:
            await processing_msg.edit_text(f"❌ Error processing URL: {str(e)}")
            print(f"Error: {e}")
        finally:
            # Clean up temp directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Error cleaning up temp dir: {e}")

    def is_valid_url(self, text: str) -> bool:
        """Check if text is a valid URL"""
        return text.startswith(('http://', 'https://')) and '.' in text

    def is_youtube_url(self, url: str) -> bool:
        """Check if URL is from YouTube"""
        return 'youtube.com' in url or 'youtu.be' in url
    
    def is_social_media_url(self, url: str) -> str:
        """Detect social media platform type"""
        if 'pinterest.com' in url:
            return 'pinterest'
        elif 'deviantart.com' in url:
            return 'deviantart'
        elif 'flickr.com' in url:
            return 'flickr'
        elif 'reddit.com' in url or 'redd.it' in url:
            return 'reddit'
        elif 'tumblr.com' in url:
            return 'tumblr'
        elif 'behance.net' in url:
            return 'behance'
        elif 'linkedin.com' in url:
            return 'linkedin'
        elif 't.me' in url:
            return 'telegram'
        elif 'instagram.com' in url:
            return 'instagram'
        elif 'twitter.com' in url or 'x.com' in url:
            return 'twitter'
        elif 'facebook.com' in url:
            return 'facebook'
        elif 'tiktok.com' in url:
            return 'tiktok'
        else:
            return 'unknown'

    def find_ffmpeg(self) -> Optional[str]:
        """Find ffmpeg executable in common locations"""
        common_paths = [
            '/usr/local/bin/ffmpeg',
            '/opt/homebrew/bin/ffmpeg', 
            '/usr/bin/ffmpeg',
            'ffmpeg'  # Check if it's in PATH
        ]
        
        for path in common_paths:
            try:
                result = subprocess.run([path, '-version'], 
                                      capture_output=True, 
                                      timeout=5)
                if result.returncode == 0:
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                continue
        return None

    async def analyze_instagram_content(self, url: str) -> dict:
        """Analyze Instagram URL to determine content type (video/image)"""
        try:
            # Use yt-dlp to quickly analyze the content without downloading
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                '--no-warnings',
                url
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=15.0)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {'type': 'unknown', 'reason': 'timeout'}
            
            if process.returncode == 0:
                try:
                    info = json.loads(stdout.decode())
                    
                    # Analyze the content
                    has_video = bool(info.get('duration')) or bool(info.get('vcodec', '').strip('none'))
                    has_audio = bool(info.get('acodec', '').strip('none'))
                    width = info.get('width', 0)
                    height = info.get('height', 0)
                    ext = info.get('ext', '').lower()
                    
                    # Determine content type
                    if has_video or ext in ['mp4', 'webm', 'mov']:
                        content_type = 'video'
                        best_tool = 'yt-dlp'  # Better for videos
                    elif ext in ['jpg', 'jpeg', 'png', 'gif'] or (width > 0 and height > 0 and not has_video):
                        content_type = 'image'
                        best_tool = 'gallery-dl'  # Better for images
                    else:
                        content_type = 'mixed'
                        best_tool = 'gallery-dl'  # Default for Instagram
                    
                    return {
                        'type': content_type,
                        'best_tool': best_tool,
                        'has_video': has_video,
                        'has_audio': has_audio,
                        'duration': info.get('duration'),
                        'format': ext,
                        'resolution': f"{width}x{height}" if width and height else None,
                        'title': info.get('title', ''),
                        'uploader': info.get('uploader', '')
                    }
                    
                except json.JSONDecodeError:
                    return {'type': 'unknown', 'reason': 'invalid_json'}
            else:
                # Check if it's an authentication error
                error_msg = stderr.decode().lower()
                if 'login' in error_msg or 'auth' in error_msg:
                    return {'type': 'auth_required', 'reason': 'authentication_needed'}
                else:
                    return {'type': 'unknown', 'reason': 'analysis_failed'}
                    
        except Exception as e:
            logging.error(f"Error analyzing Instagram content: {e}")
            return {'type': 'unknown', 'reason': str(e)}

    async def merge_video_audio_ffmpeg(self, video_file: Path, audio_file: Path, output_file: Path) -> bool:
        """Merge video and audio files using ffmpeg"""
        ffmpeg_path = self.find_ffmpeg()
        if not ffmpeg_path:
            logging.warning("ffmpeg not found, cannot merge video/audio")
            return False
            
        try:
            cmd = [
                ffmpeg_path,
                '-i', str(video_file),
                '-i', str(audio_file),
                '-c:v', 'copy',  # Copy video without re-encoding
                '-c:a', 'aac',   # Re-encode audio to AAC
                '-map', '0:v:0', # Map first video stream
                '-map', '1:a:0', # Map first audio stream
                '-movflags', '+faststart',  # Optimize for streaming
                '-y',  # Overwrite output file
                str(output_file)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
            
            if process.returncode == 0 and output_file.exists():
                logging.info(f"Successfully merged video/audio with ffmpeg: {output_file}")
                return True
            else:
                logging.error(f"ffmpeg merge failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logging.error(f"Error in ffmpeg merge: {e}")
            return False

    async def get_youtube_formats(self, url: str) -> Optional[list]:
        """Get available formats for YouTube video"""
        try:
            cmd = [
                'yt-dlp',
                '--list-formats',
                '--no-warnings',
                url
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=15.0)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return None

            if process.returncode != 0:
                return None

            # Parse format list and extract formats with audio or pre-combined
            quality_set = set()
            format_mapping = {}
            lines = stdout.decode().split('\n')

            for line in lines:
                if line.startswith('format code') or line.startswith('----') or not line.strip():
                    continue

                # Look for video formats (include both combined and video-only)
                if ('mp4' in line or 'webm' in line) and 'audio only' not in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        format_id = parts[0]

                        # Extract quality from the line
                        quality = None
                        if '2160' in line or '4K' in line:
                            quality = '2160p'
                        elif '1440' in line:
                            quality = '1440p'
                        elif '1080' in line:
                            quality = '1080p'
                        elif '720' in line:
                            quality = '720p'
                        elif '480' in line:
                            quality = '480p'
                        elif '360' in line:
                            quality = '360p'
                        elif '240' in line:
                            quality = '240p'
                        elif '144' in line:
                            quality = '144p'
                        else:
                            continue

                        # Include all video qualities (will combine with audio automatically)
                        if quality and quality not in ['144p'] and format_id not in ['140', '251', '249', '250', '17', '36']:
                            quality_set.add(quality)
                            # Prioritize formats that already have audio, but include video-only too
                            if quality not in format_mapping or 'video only' not in line:
                                format_mapping[quality] = format_id

            # Always add audio-only option
            quality_set.add('Audio Only')
            format_mapping['Audio Only'] = '140'  # M4A audio format

            # Convert to list and sort by quality (put Audio Only last)
            quality_order = {'2160p': 7, '1440p': 6, '1080p': 5, '720p': 4, '480p': 3, '360p': 2, '240p': 1, 'Audio Only': 0}
            available_qualities = sorted(list(quality_set),
                                       key=lambda x: quality_order.get(x, 0),
                                       reverse=True)

            # Create formats list
            formats = []
            for quality in available_qualities:
                formats.append({
                    'id': format_mapping[quality],
                    'resolution': quality,
                    'note': quality,
                    'quality': quality
                })

            return formats[:6]  # Return top 6 formats

        except Exception as e:
            logging.error(f"Error getting YouTube formats: {e}")
            return None

    async def download_with_gallery_dl(self, url: str, temp_dir: str) -> Optional[dict]:
        """Download media using gallery-dl"""
        try:
            cmd = [
                'gallery-dl',
                '--write-info-json',
                '--directory', temp_dir,
                url
            ]
            
            # Add Instagram cookies if available
            if ('instagram.com' in url) and INSTAGRAM_COOKIES_FILE and Path(INSTAGRAM_COOKIES_FILE).exists():
                cmd.extend(['--cookies', INSTAGRAM_COOKIES_FILE])
                logging.info("Using Instagram cookies for authentication")
            
            # Add Reddit API credentials if available
            elif ('reddit.com' in url or 'redd.it' in url) and REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET:
                # Create temporary config for Reddit API
                config_content = f"""{{
    "extractor": {{
        "reddit": {{
            "client-id": "{REDDIT_CLIENT_ID}",
            "client-secret": "{REDDIT_CLIENT_SECRET}",
            "user-agent": "{REDDIT_USER_AGENT}"
        }}
    }}
}}"""
                config_file = Path(temp_dir) / "gallery-dl-config.json"
                with open(config_file, 'w') as f:
                    f.write(config_content)
                
                cmd.extend(['--config', str(config_file)])
                logging.info("Using Reddit API credentials for better access")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Set timeout based on platform (Reddit needs more time)
            timeout = 45.0 if ('reddit.com' in url or 'redd.it' in url) else 20.0
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                logging.error(f"gallery-dl timeout after {timeout}s for URL: {url}")
                return None

            if process.returncode == 0:
                return await self.process_downloaded_files(temp_dir, 'gallery-dl')
            else:
                error_msg = stderr.decode()
                if "rate limit" in error_msg.lower():
                    logging.warning("Reddit rate limit hit - consider adding Reddit API credentials")
                elif "login page" in error_msg.lower():
                    logging.warning("Instagram/platform requires authentication - consider adding cookies")
                logging.error(f"gallery-dl failed: {error_msg}")

        except Exception as e:
            logging.error(f"Gallery-dl error: {e}")

        return None

    async def download_with_yt_dlp(self, url: str, temp_dir: str) -> Optional[dict]:
        """Download media using yt-dlp"""
        try:
            # Detect if ffmpeg is available for better merging
            ffmpeg_available = self.find_ffmpeg() is not None
            
            # Special handling for platforms that often have separate video/audio
            if 'reddit.com' in url or 'redd.it' in url or 'facebook.com' in url:
                if ffmpeg_available:
                    # Use separate downloads when ffmpeg is available for better quality
                    format_selector = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
                else:
                    # Prefer combined streams when ffmpeg is not available
                    format_selector = 'best[height<=720][acodec!=none]/bestvideo[height<=720]+bestaudio/best[height<=720]/best'
            else:
                format_selector = 'best[height<=720][acodec!=none]/best[acodec!=none]/best'
            
            cmd = [
                'yt-dlp',
                '--write-info-json',
                '--format', format_selector,
                '--max-filesize', '45M',  # Telegram limit
                '--output', f'{temp_dir}/%(title)s.%(ext)s',
                url
            ]
            
            # Only add merge format if ffmpeg is not available (let our custom merge handle it)
            if not ffmpeg_available:
                cmd.extend(['--merge-output-format', 'mp4'])

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Set timeout based on platform and ffmpeg availability
            if 'reddit.com' in url or 'redd.it' in url or 'facebook.com' in url:
                timeout = 60.0  # Reddit/Facebook videos need more time
            else:
                timeout = 30.0
                
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                logging.error(f"yt-dlp timeout after {timeout}s for URL: {url}")
                return None

            if process.returncode == 0:
                return await self.process_downloaded_files(temp_dir, 'yt-dlp')
            else:
                logging.error(f"yt-dlp failed: {stderr.decode()}")

        except Exception as e:
            logging.error(f"yt-dlp error: {e}")

        return None

    async def process_downloaded_files(self, temp_dir: str, source: str) -> Optional[dict]:
        """Process downloaded files and extract info"""
        temp_path = Path(temp_dir)
        media_files = []
        info_files = []
        video_files = []
        audio_files = []

        # Find downloaded files
        for file_path in temp_path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in ['.mp4', '.webm', '.mov', '.avi', '.mkv']:
                    # Check if it's video-only by looking for audio counterpart
                    audio_counterpart = file_path.with_suffix('.m4a')
                    if audio_counterpart.exists():
                        video_files.append(file_path)
                    else:
                        media_files.append(file_path)
                elif ext in ['.m4a', '.mp3', '.aac', '.opus']:
                    # Check if it's audio-only by looking for video counterpart
                    video_counterpart = file_path.with_name(file_path.stem.replace('.m4a', '')).with_suffix('.mp4')
                    if video_counterpart.exists():
                        audio_files.append(file_path)
                    else:
                        media_files.append(file_path)
                elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    media_files.append(file_path)
                elif ext == '.json':
                    info_files.append(file_path)

        # Try to merge video+audio files with ffmpeg if available
        if video_files and audio_files and len(video_files) == len(audio_files):
            ffmpeg_path = self.find_ffmpeg()
            if ffmpeg_path:
                logging.info("Found separate video/audio files, attempting ffmpeg merge...")
                for i, video_file in enumerate(video_files):
                    if i < len(audio_files):
                        audio_file = audio_files[i]
                        merged_file = video_file.with_name(f"{video_file.stem}_merged.mp4")
                        
                        if await self.merge_video_audio_ffmpeg(video_file, audio_file, merged_file):
                            media_files.append(merged_file)
                            logging.info(f"Successfully merged: {merged_file}")
                        else:
                            # Fallback: keep original files
                            media_files.extend([video_file, audio_file])
                            logging.warning("ffmpeg merge failed, keeping separate files")
            else:
                # No ffmpeg available, keep separate files
                media_files.extend(video_files)
                media_files.extend(audio_files)
                logging.warning("ffmpeg not available, keeping separate video/audio files")
        else:
            # Add any remaining video/audio files
            media_files.extend(video_files)
            media_files.extend(audio_files)

        if not media_files:
            return None

        # Read metadata from info files
        metadata = {}
        if info_files:
            try:
                async with aiofiles.open(info_files[0], 'r', encoding='utf-8') as f:
                    content = await f.read()
                    metadata = json.loads(content)
            except Exception as e:
                print(f"Error reading metadata: {e}")

        return {
            'files': media_files,
            'metadata': metadata,
            'source': source
        }

    async def send_media_to_user(self, update: Update, media_info: dict):
        """Send downloaded media to user with formatted description"""
        files = media_info['files']
        metadata = media_info['metadata']

        # Format description with Geist Mono font
        import sys
        print(f"MAIN DEBUG - About to format description", file=sys.stderr)
        print(f"MAIN DEBUG - Metadata keys: {list(metadata.keys()) if metadata else 'None'}", file=sys.stderr)
        if metadata:
            print(f"MAIN DEBUG - Title: '{metadata.get('title', '')}'", file=sys.stderr)
            print(f"MAIN DEBUG - Uploader: '{metadata.get('uploader', '')}'", file=sys.stderr)
            print(f"MAIN DEBUG - Description: '{metadata.get('description', '')}'", file=sys.stderr)
        description = self.format_description(metadata)
        print(f"MAIN DEBUG - Final description: '{description}'", file=sys.stderr)

        for file_path in files:
            try:
                # Check if file exists
                if not file_path.exists():
                    await update.message.reply_text(f"❌ File not found: {file_path.name}")
                    continue

                file_size = file_path.stat().st_size

                # Check file size (Telegram limit is 50MB)
                if file_size > 50 * 1024 * 1024:  # 50MB
                    await update.message.reply_text(f"❌ File too large to send: {file_path.name} ({file_size / (1024*1024):.1f}MB)")
                    continue

                # Read file content first
                file_content = None
                try:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                except Exception as read_error:
                    await update.message.reply_text(f"❌ Error reading file: {str(read_error)}")
                    continue

                if not file_content:
                    await update.message.reply_text(f"❌ Empty file: {file_path.name}")
                    continue

                # Determine file type and send accordingly
                file_ext = file_path.suffix.lower()

                if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    await update.message.reply_photo(
                        photo=file_content,
                        caption=description,
                        parse_mode=ParseMode.MARKDOWN
                    )
                elif file_ext in ['.mp4', '.webm', '.mov', '.avi']:
                    await update.message.reply_video(
                        video=file_content,
                        caption=description,
                        parse_mode=ParseMode.MARKDOWN
                    )
                elif file_ext in ['.mp3', '.m4a', '.wav', '.ogg']:
                    await update.message.reply_audio(
                        audio=file_content,
                        caption=description,
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    # Send as document
                    await update.message.reply_document(
                        document=file_content,
                        filename=file_path.name,
                        caption=description,
                        parse_mode=ParseMode.MARKDOWN
                    )

            except Exception as e:
                await update.message.reply_text(f"❌ Error sending file: {str(e)}")
                print(f"Error sending file {file_path}: {e}")

        # No separate copyable text message - everything is in caption now

    async def send_copyable_description(self, update: Update, metadata: dict):
        """Send media description as copyable text - only title and description"""
        if not metadata:
            return

        # Extract info
        title = metadata.get('title', '')
        description = metadata.get('description', '')
        webpage_url = metadata.get('webpage_url', '')

        # Check if it's YouTube
        is_youtube = 'youtube.com' in webpage_url or 'youtu.be' in webpage_url

        # For YouTube: only title and source (creator/channel)
        if is_youtube:
            copyable_text = ""
            if title and title.strip():
                copyable_text = title.strip()

            # Get source - prefer channel, then uploader
            source = metadata.get('channel', metadata.get('uploader', ''))
            if source and source.strip():
                if copyable_text:
                    copyable_text += f"\n\n{source.strip()}"
                else:
                    copyable_text = source.strip()
        else:
            # For other platforms: title and description
            # Clean up description - only remove if it's ONLY a URL or too short
            if description:
                desc_clean = description.strip()
                # Only remove if the whole description is just a URL
                words = desc_clean.split()
                if len(words) == 1 and words[0].startswith('http'):
                    description = ''
                # Remove if too short
                elif len(desc_clean) < 10:
                    description = ''

            copyable_text = ""
            if title and title.strip():
                copyable_text = title.strip()

            if description and description.strip():
                if copyable_text:
                    copyable_text += f"\n\n{description.strip()}"
                else:
                    copyable_text = description.strip()

        # Only send if we have meaningful content
        if copyable_text.strip() and len(copyable_text.strip()) > 5:
            await update.message.reply_text(copyable_text)

    def format_description(self, metadata: dict) -> str:
        """Format media description - copyable for YouTube, monospace for others"""
        if not metadata:
            return "```\n📥 Media downloaded successfully\n```"

        # Handle both yt-dlp and gallery-dl metadata formats
        # yt-dlp format
        title = metadata.get('title', '')
        description = metadata.get('description', '')
        source = (metadata.get('channel') or
                 metadata.get('uploader') or
                 metadata.get('uploader_id', '').replace('_', ' ').title())

        # gallery-dl format (Twitter, Instagram, etc.)
        if not title and not source and not description:
            # Twitter/X format
            if 'author' in metadata:
                author = metadata.get('author', {})
                if isinstance(author, dict):
                    source = author.get('name') or author.get('username', '')
                else:
                    source = str(author)
                description = metadata.get('content', '')
                # Use the first part of content as title if no separate title
                if description and not title:
                    title = description[:60] + "..." if len(description) > 60 else description

            # Facebook format
            elif 'username' in metadata:
                source = metadata.get('username', '')
                # For Facebook, we don't have much metadata

        # Clean source
        if not source:
            source = ''

        # Clean up description - only remove if it's ONLY a URL or too short
        if description:
            desc_clean = description.strip()
            # Only remove if the whole description is just a URL
            words = desc_clean.split()
            if len(words) == 1 and words[0].startswith('http'):
                description = ''
            # Remove if too short
            elif len(desc_clean) < 10:
                description = ''

        formatted_desc = "```\n"
        has_content = False

        if title and title.strip():
            formatted_desc += f"📁 {title.strip()}\n"
            has_content = True

        if source and source.strip():
            if has_content:
                formatted_desc += f"\n👤 {source.strip()}\n"
            else:
                formatted_desc += f"👤 {source.strip()}\n"
            has_content = True

        # Add description if meaningful
        if description and description.strip():
            desc_preview = description.strip()[:200] + "..." if len(description.strip()) > 200 else description.strip()
            if has_content:
                formatted_desc += f"\n📝 {desc_preview}\n"
            else:
                formatted_desc += f"📝 {desc_preview}\n"
            has_content = True

        # If no meaningful content, show simple download message
        if not has_content:
            formatted_desc += "📥 Media downloaded\n"

        formatted_desc += "```"
        return formatted_desc

    async def quality_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle quality selection callback"""
        query = update.callback_query

        try:
            await query.answer()
        except:
            pass  # Ignore callback answer errors

        data_parts = query.data.split(':', 2)
        if len(data_parts) != 3 or data_parts[0] != 'quality':
            try:
                await query.edit_message_text("❌ Invalid selection")
            except:
                pass
            return

        format_id = data_parts[1]
        url = data_parts[2]

        user = query.from_user
        logging.info(f"Quality selected by {user.first_name}: {format_id} for {url}")

        # Update message to show downloading
        try:
            await query.edit_message_text("🔄 Downloading your selected quality...")
        except:
            # If editing fails, send a new message
            await query.message.reply_text("🔄 Downloading your selected quality...")

        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="setupia_")

        try:
            # Download with selected format
            media_info = await self.download_with_yt_dlp_format(url, temp_dir, format_id)

            if media_info:
                await self.send_media_to_user_from_callback(query, media_info)
                # Delete the quality selection message
                try:
                    await query.message.delete()
                except:
                    pass
            else:
                await query.edit_message_text("❌ Download failed. The selected quality might not be available anymore.")

        except Exception as e:
            await query.edit_message_text(f"❌ Error downloading: {str(e)}")
            logging.error(f"Error in quality callback: {e}")
        finally:
            # Clean up
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logging.error(f"Error cleaning up temp dir: {e}")

    async def download_with_yt_dlp_format(self, url: str, temp_dir: str, format_id: str) -> Optional[dict]:
        """Download media using yt-dlp with specific format"""
        try:
            if format_id == "best" or format_id == "Best":
                # Special handling for Reddit to ensure merged audio+video
                if 'reddit.com' in url or 'redd.it' in url:
                    format_selector = 'best[height<=720][acodec!=none]/bestvideo[height<=720]+bestaudio/best'
                else:
                    format_selector = 'best[height<=720][acodec!=none]/best[acodec!=none]/best'
            elif format_id == "140":  # Audio only
                format_selector = 'bestaudio[ext=m4a]/best'
            else:
                # For video formats, try to get combined streams first, then video-only
                format_selector = f'{format_id}[acodec!=none]/{format_id}/best[height<=720][acodec!=none]/best'

            cmd = [
                'yt-dlp',
                '--write-info-json',
                '--format', format_selector,
                '--max-filesize', '45M',
                '--output', f'{temp_dir}/%(title)s.%(ext)s',
                '--merge-output-format', 'mp4',  # Ensure merged output
                '--no-warnings',
                url
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=45.0)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                logging.error(f"yt-dlp timeout for format {format_id}")
                return None

            if process.returncode == 0:
                return await self.process_downloaded_files(temp_dir, 'yt-dlp')
            else:
                # Log the error and try best fallback
                error_msg = stderr.decode()
                logging.error(f"yt-dlp failed for format {format_id}: {error_msg}")
                return await self.fallback_download(url, temp_dir)

        except Exception as e:
            logging.error(f"yt-dlp error for format {format_id}: {e}")
            return await self.fallback_download(url, temp_dir)

        return None

    async def fallback_download(self, url: str, temp_dir: str) -> Optional[dict]:
        """Fallback download with best available quality"""
        try:
            cmd = [
                'yt-dlp',
                '--write-info-json',
                '--format', 'best[height<=720][acodec!=none]/best[acodec!=none]/best',
                '--output', f'{temp_dir}/%(title)s_fallback.%(ext)s',
                '--no-warnings',
                url
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return None

            if process.returncode == 0:
                return await self.process_downloaded_files(temp_dir, 'yt-dlp-fallback')

        except Exception as e:
            logging.error(f"Fallback download error: {e}")

        return None

    async def send_media_to_user_from_callback(self, query, media_info: dict):
        """Send downloaded media to user from callback query"""
        files = media_info['files']
        metadata = media_info['metadata']

        # Format description with Geist Mono font
        description = self.format_description(metadata)

        for file_path in files:
            try:
                if not file_path.exists():
                    await query.message.reply_text(f"❌ File not found: {file_path.name}")
                    continue

                file_size = file_path.stat().st_size

                if file_size > 50 * 1024 * 1024:  # 50MB
                    await query.message.reply_text(f"❌ File too large: {file_path.name} ({file_size / (1024*1024):.1f}MB)")
                    continue

                # Read file content
                with open(file_path, 'rb') as f:
                    file_content = f.read()

                if not file_content:
                    await query.message.reply_text(f"❌ Empty file: {file_path.name}")
                    continue

                file_ext = file_path.suffix.lower()

                if file_ext in ['.mp4', '.webm', '.mov', '.avi']:
                    await query.message.reply_video(
                        video=file_content,
                        caption=description,
                        parse_mode=ParseMode.MARKDOWN
                    )
                elif file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    await query.message.reply_photo(
                        photo=file_content,
                        caption=description,
                        parse_mode=ParseMode.MARKDOWN
                    )
                elif file_ext in ['.mp3', '.m4a', '.wav', '.ogg']:
                    await query.message.reply_audio(
                        audio=file_content,
                        caption=description,
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await query.message.reply_document(
                        document=file_content,
                        filename=file_path.name,
                        caption=description,
                        parse_mode=ParseMode.MARKDOWN
                    )

            except Exception as e:
                await query.message.reply_text(f"❌ Error sending file: {str(e)}")
                logging.error(f"Error sending file {file_path}: {e}")

        # No separate copyable text message - everything is in caption now

    async def send_copyable_description_callback(self, query, metadata: dict):
        """Send media description as copyable text from callback - only title and description"""
        if not metadata:
            return

        # Extract info
        title = metadata.get('title', '')
        description = metadata.get('description', '')
        webpage_url = metadata.get('webpage_url', '')

        # Check if it's YouTube
        is_youtube = 'youtube.com' in webpage_url or 'youtu.be' in webpage_url

        # For YouTube: only title and source (creator/channel)
        if is_youtube:
            copyable_text = ""
            if title and title.strip():
                copyable_text = title.strip()

            # Get source - prefer channel, then uploader
            source = metadata.get('channel', metadata.get('uploader', ''))
            if source and source.strip():
                if copyable_text:
                    copyable_text += f"\n\n{source.strip()}"
                else:
                    copyable_text = source.strip()
        else:
            # For other platforms: title and description
            # Clean up description - only remove if it's ONLY a URL or too short
            if description:
                desc_clean = description.strip()
                # Only remove if the whole description is just a URL
                words = desc_clean.split()
                if len(words) == 1 and words[0].startswith('http'):
                    description = ''
                # Remove if too short
                elif len(desc_clean) < 10:
                    description = ''

            copyable_text = ""
            if title and title.strip():
                copyable_text = title.strip()

            if description and description.strip():
                if copyable_text:
                    copyable_text += f"\n\n{description.strip()}"
                else:
                    copyable_text = description.strip()

        # Only send if we have meaningful content
        if copyable_text.strip() and len(copyable_text.strip()) > 5:
            await query.message.reply_text(copyable_text)

    def run(self):
        """Start the bot"""
        print("🚀 Starting Setupia AI Saver bot...")
        print("   Bot: @SetupiaSaverBot")
        print("   Ready to receive URLs!")
        print("Press Ctrl+C to stop")
        try:
            self.app.run_polling()
        except KeyboardInterrupt:
            print("\n👋 Bot stopped by user")
        except Exception as e:
            print(f"❌ Bot error: {e}")
            raise

if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")

    if not token:
        print("❌ BOT_TOKEN not found in environment variables")
        exit(1)

    bot = SetupiaAISaver(token)
    bot.run()