from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("toimg", "JayLeo", "A plugin to render text to image.", "0.1.0")
class ToImgPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("toimg")
    async def toimg_command(self, event: AstrMessageEvent, text: str):
        """
        Renders text to an image using an LLM and HTML.
        Args:
            text(string): The text to render.
        """
        try:
            # 1. Acknowledge the command and inform the user about the process
            yield event.plain_result("Received! Generating HTML with LLM and rendering to image...")

            # 2. Get the LLM provider
            provider = self.context.get_using_provider()
            if not provider:
                yield event.plain_result("LLM provider not configured. Please configure a provider in the settings.")
                return

            # 3. Create a prompt for the LLM to generate HTML
            prompt = f"""Please generate a self-contained HTML snippet which is easily viewable on mobile devices for the following text. It should be visually appealing and easy to read. Only return raw HTML code.
            Ensure that mathematical formulas are rendered correctly using MathJax. Include the MathJax CDN script and configure it to process LaTeX math.
            Example MathJax configuration:
            <script type="text/javascript" id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <script>
            MathJax = {{
              tex: {{
                inlineMath: [['$', '$'], ['\\(', '\\)']]
              }},
              svg: {{
                fontCache: 'global'
              }}
            }};
            </script>
            \n\n{text}"""

            # 4. Call the LLM to get the HTML content
            response = await provider.text_chat(prompt=prompt, session_id=None, contexts=[])
            html_content = response.completion_text

            if not html_content:
                yield event.plain_result("LLM returned empty content. Cannot generate image.")
                return

            # 5. Render the HTML to an image
            image_url = await self.html_render(html_content, {"text": text})

            # 6. Send the image back to the user
            yield event.image_result(image_url)

        except Exception as e:
            logger.error(f"Error in toimg plugin: {e}")
            yield event.plain_result(f"An error occurred: {e}")

    async def terminate(self):
        pass
