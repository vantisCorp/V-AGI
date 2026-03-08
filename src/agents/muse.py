"""
MUSE Agent - Creative Content Generation

Provides:
- Creative writing and storytelling
- Art and design generation
- Music composition
- Poetry and literature
- Marketing copy generation
- Brand identity creation
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from loguru import logger

from agents.base_agent import (
    AgentCapabilities,
    AgentResponse,
    AgentStatus,
    BaseAgent,
    Task,
    TaskPriority,
)


class ContentType(Enum):
    """Types of creative content."""

    STORY = "story"
    POEM = "poem"
    ARTICLE = "article"
    MARKETING_COPY = "marketing_copy"
    BRAND_IDENTITY = "brand_identity"
    ART_DESCRIPTION = "art_description"
    MUSIC_COMPOSITION = "music_composition"
    SCRIPT = "script"
    SOCIAL_MEDIA = "social_media"


@dataclass
class CreativeContent:
    """Creative content output."""

    content_type: ContentType
    title: str
    content: str
    style: str
    mood: str
    target_audience: str
    generated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert content to dictionary."""
        return {
            "content_type": self.content_type.value,
            "title": self.title,
            "content": self.content,
            "style": self.style,
            "mood": self.mood,
            "target_audience": self.target_audience,
            "generated_at": self.generated_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class CreativeBrief:
    """Creative brief for content generation."""

    topic: str
    content_type: ContentType
    style: str = "professional"
    mood: str = "neutral"
    target_audience: str = "general"
    length: str = "medium"
    keywords: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)


class MuseAgent(BaseAgent):
    """
    MUSE Agent - Creative content generation specialist.

    Capabilities:
    - Creative writing and storytelling
    - Poetry and literature
    - Marketing copy generation
    - Brand identity creation
    - Social media content
    - Script writing
    - Art and design descriptions
    - Music composition
    """

    def __init__(self, agent_id: str = "muse"):
        """Initialize MUSE agent."""
        capabilities = AgentCapabilities(
            name="MUSE",
            description="Creative content generation agent",
            skills=[
                "creative_writing",
                "storytelling",
                "poetry",
                "marketing_copy",
                "brand_identity",
                "social_media",
                "script_writing",
                "art_generation",
            ],
            tools=["language_model", "image_generator", "music_generator", "style_analyzer"],
            max_concurrent_tasks=5,
            specialization="creative",
        )

        super().__init__(agent_id=agent_id, capabilities=capabilities, clearance_level=1)

        # Content templates (placeholder strings - actual templates defined as methods below)
        self.content_templates = {
            ContentType.STORY: "story_template",
            ContentType.POEM: "poem_template",
            ContentType.ARTICLE: "article_template",
            ContentType.MARKETING_COPY: "marketing_copy_template",
            ContentType.SOCIAL_MEDIA: "social_media_template",
            ContentType.SCRIPT: "script_template",
        }

        # Style presets
        self.style_presets = {
            "professional": "Formal, clear, and business-oriented",
            "casual": "Conversational, friendly, and approachable",
            "dramatic": "Emotional, intense, and theatrical",
            "humorous": "Funny, witty, and entertaining",
            "minimalist": "Simple, clean, and straightforward",
            "artistic": "Expressive, imaginative, and creative",
            "technical": "Precise, detailed, and informative",
        }

        logger.info(f"MUSE agent initialized: {agent_id}")

    async def validate_task(self, task: Task) -> bool:
        """
        Validate if this agent can handle the task.

        Args:
            task: Task to validate

        Returns:
            True if agent can handle the task
        """
        valid_task_types = [
            "generate_story",
            "generate_poem",
            "write_article",
            "create_marketing_copy",
            "design_brand_identity",
            "generate_social_media",
            "write_script",
            "describe_art",
        ]

        task_type = task.parameters.get("task_type", "")
        return task_type in valid_task_types

    async def execute_task(self, task: Task) -> AgentResponse:
        """
        Execute a creative content generation task.

        Args:
            task: Task to execute

        Returns:
            Agent response with creative content
        """
        start_time = datetime.utcnow()
        await self.set_status(AgentStatus.PROCESSING)
        await self.add_task(task.id)

        try:
            task_type = task.parameters.get("task_type", "")

            if task_type == "generate_story":
                result = await self._generate_story(task)
            elif task_type == "generate_poem":
                result = await self._generate_poem(task)
            elif task_type == "write_article":
                result = await self._write_article(task)
            elif task_type == "create_marketing_copy":
                result = await self._create_marketing_copy(task)
            elif task_type == "design_brand_identity":
                result = await self._design_brand_identity(task)
            elif task_type == "generate_social_media":
                result = await self._generate_social_media(task)
            elif task_type == "write_script":
                result = await self._write_script(task)
            elif task_type == "describe_art":
                result = await self._describe_art(task)
            else:
                result = {"error": f"Unknown task type: {task_type}", "status": "error"}

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            response = AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                status="success",
                result=result,
                execution_time=execution_time,
                metadata={"task_type": task_type},
            )

            await self.set_status(AgentStatus.IDLE)
            await self.remove_task(task.id)
            self.record_response(response)

            return response

        except Exception as e:
            logger.error(f"MUSE agent error: {e}")

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            response = AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                status="error",
                error=str(e),
                execution_time=execution_time,
            )

            await self.set_status(AgentStatus.ERROR)
            await self.remove_task(task.id)
            self.record_response(response)

            return response

    async def _generate_story(self, task: Task) -> Dict[str, Any]:
        """
        Generate a creative story.

        Args:
            task: Task with story parameters

        Returns:
            Generated story
        """
        topic = task.parameters.get("topic", "A mysterious adventure")
        genre = task.parameters.get("genre", "fantasy")
        style = task.parameters.get("style", "professional")
        length = task.parameters.get("length", "medium")
        characters = task.parameters.get("characters", [])

        # Generate story based on parameters
        story_content = self._create_story_content(
            topic=topic, genre=genre, style=style, length=length, characters=characters
        )

        content = CreativeContent(
            content_type=ContentType.STORY,
            title=f"Story: {topic}",
            content=story_content,
            style=style,
            mood=genre,
            target_audience="general",
            metadata={"genre": genre, "length": length, "characters": characters},
        )

        return {
            "title": content.title,
            "content": content.content,
            "genre": genre,
            "style": style,
            "length": length,
            "word_count": len(content.content.split()),
            "metadata": content.metadata,
        }

    def _create_story_content(
        self, topic: str, genre: str, style: str, length: str, characters: List[str]
    ) -> str:
        """Create story content."""
        # Simplified story generation (placeholder)
        # In production, use advanced language models

        intro = f"In the realm of {genre.lower()}, {topic.lower()} began to unfold."

        if characters:
            char_intro = f" Our protagonists, {', '.join(characters)}, found themselves at the heart of this mystery."
        else:
            char_intro = (
                " The adventure was just beginning for the brave souls who dared to explore."
            )

        body = """
        
        As the journey progressed, challenges emerged that tested their resolve and courage. 
        Each step revealed new mysteries and unexpected discoveries that would change everything 
        they thought they knew about the world around them.
        
        """

        ending = """
        
        And so, the adventure concluded, but the memories and lessons learned would last forever. 
        The journey had transformed them, and they emerged stronger, wiser, and ready for whatever 
        challenges lay ahead.
        """

        return intro + char_intro + body + ending

    async def _generate_poem(self, task: Task) -> Dict[str, Any]:
        """
        Generate a poem.

        Args:
            task: Task with poem parameters

        Returns:
            Generated poem
        """
        topic = task.parameters.get("topic", "Nature")
        style = task.parameters.get("style", "lyrical")
        rhyme_scheme = task.parameters.get("rhyme_scheme", "ABAB")
        stanzas = task.parameters.get("stanzas", 3)

        # Generate poem
        poem_content = self._create_poem_content(topic=topic, style=style, stanzas=stanzas)

        content = CreativeContent(
            content_type=ContentType.POEM,
            title=f"Poem: {topic}",
            content=poem_content,
            style=style,
            mood="expressive",
            target_audience="general",
            metadata={"rhyme_scheme": rhyme_scheme, "stanzas": stanzas},
        )

        return {
            "title": content.title,
            "content": content.content,
            "style": style,
            "rhyme_scheme": rhyme_scheme,
            "stanzas": stanzas,
            "lines": len(content.content.split("\n")),
            "metadata": content.metadata,
        }

    def _create_poem_content(self, topic: str, style: str, stanzas: int) -> str:
        """Create poem content."""
        # Simplified poem generation (placeholder)

        poem_lines = []
        for i in range(stanzas):
            poem_lines.extend(
                [
                    f"In {topic.lower()}'s embrace so true,",
                    f"Whispers of ancient times break through,",
                    f"Nature's canvas painted with grace,",
                    f"In this moment, time leaves no trace.",
                ]
            )
            poem_lines.append("")  # Empty line between stanzas

        return "\n".join(poem_lines)

    async def _write_article(self, task: Task) -> Dict[str, Any]:
        """
        Write an article.

        Args:
            task: Task with article parameters

        Returns:
            Written article
        """
        topic = task.parameters.get("topic", "Technology Trends")
        tone = task.parameters.get("tone", "informative")
        word_count = task.parameters.get("word_count", 500)

        # Generate article
        article_content = self._create_article_content(
            topic=topic, tone=tone, word_count=word_count
        )

        content = CreativeContent(
            content_type=ContentType.ARTICLE,
            title=f"Article: {topic}",
            content=article_content,
            style=tone,
            mood="informative",
            target_audience="general",
            metadata={"tone": tone, "word_count_target": word_count},
        )

        return {
            "title": content.title,
            "content": content.content,
            "tone": tone,
            "word_count": len(content.content.split()),
            "metadata": content.metadata,
        }

    def _create_article_content(self, topic: str, tone: str, word_count: int) -> str:
        """Create article content."""
        # Simplified article generation (placeholder)

        title = f"{topic}: An Overview"

        introduction = f"""
        
        {topic} has become increasingly important in today's rapidly evolving landscape. 
        This article explores the key aspects, trends, and implications of this topic.
        
        """

        body = f"""
        
        Understanding {topic.lower()} requires examining its various components and how they 
        interact with broader systems. Recent developments have shown significant progress 
        in this area, with new approaches emerging regularly.
        
        The implications of {topic.lower()} extend across multiple domains, affecting 
        everything from personal decisions to organizational strategies. As we continue 
        to explore this field, new opportunities and challenges will undoubtedly arise.
        
        """

        conclusion = """
        
        In conclusion, this topic represents an important area of study and practice. 
        By staying informed and engaged with ongoing developments, we can better 
        understand its impact and make informed decisions.
        
        """

        return title + introduction + body + conclusion

    async def _create_marketing_copy(self, task: Task) -> Dict[str, Any]:
        """
        Create marketing copy.

        Args:
            task: Task with marketing copy parameters

        Returns:
            Marketing copy
        """
        product = task.parameters.get("product", "Amazing Product")
        target_audience = task.parameters.get("target_audience", "general")
        tone = task.parameters.get("tone", "persuasive")
        key_benefits = task.parameters.get("key_benefits", [])

        # Generate marketing copy
        marketing_content = self._create_marketing_content(
            product=product, target_audience=target_audience, tone=tone, key_benefits=key_benefits
        )

        content = CreativeContent(
            content_type=ContentType.MARKETING_COPY,
            title=f"Marketing Copy: {product}",
            content=marketing_content,
            style=tone,
            mood="enthusiastic",
            target_audience=target_audience,
            metadata={"key_benefits": key_benefits},
        )

        return {
            "title": content.title,
            "content": content.content,
            "target_audience": target_audience,
            "tone": tone,
            "word_count": len(content.content.split()),
            "metadata": content.metadata,
        }

    def _create_marketing_content(
        self, product: str, target_audience: str, tone: str, key_benefits: List[str]
    ) -> str:
        """Create marketing content."""
        # Simplified marketing copy generation (placeholder)

        headline = f"Discover {product}: Transform Your Experience"

        subheadline = "The solution you've been waiting for is finally here."

        benefits_section = "Key Benefits:\n\n"

        if key_benefits:
            for benefit in key_benefits:
                benefits_section += f"• {benefit}\n"
        else:
            benefits_section += "• Unmatched quality and performance\n"
            benefits_section += "• Designed with your needs in mind\n"
            benefits_section += "• Backed by exceptional support\n"

        call_to_action = (
            f"\n\nDon't miss out on this incredible opportunity. Experience {product} today!"
        )

        return headline + "\n\n" + subheadline + "\n\n" + benefits_section + call_to_action

    async def _design_brand_identity(self, task: Task) -> Dict[str, Any]:
        """
        Design brand identity.

        Args:
            task: Task with brand identity parameters

        Returns:
            Brand identity design
        """
        brand_name = task.parameters.get("brand_name", "Innovate Co")
        industry = task.parameters.get("industry", "technology")
        values = task.parameters.get("values", [])
        target_audience = task.parameters.get("target_audience", "professionals")

        # Generate brand identity
        brand_identity = {
            "brand_name": brand_name,
            "tagline": self._generate_tagline(brand_name, industry),
            "brand_voice": self._define_brand_voice(values),
            "color_palette": self._suggest_color_palette(industry),
            "brand_personality": self._define_brand_personality(values, target_audience),
            "positioning_statement": self._create_positioning_statement(brand_name, industry),
            "brand_values": values if values else ["Innovation", "Quality", "Integrity"],
        }

        return {
            "brand_name": brand_identity["brand_name"],
            "tagline": brand_identity["tagline"],
            "brand_voice": brand_identity["brand_voice"],
            "color_palette": brand_identity["color_palette"],
            "brand_personality": brand_identity["brand_personality"],
            "positioning_statement": brand_identity["positioning_statement"],
            "brand_values": brand_identity["brand_values"],
        }

    def _generate_tagline(self, brand_name: str, industry: str) -> str:
        """Generate brand tagline."""
        return f"Innovating the Future of {industry.capitalize()}"

    def _define_brand_voice(self, values: List[str]) -> str:
        """Define brand voice."""
        return "Professional, innovative, and approachable"

    def _suggest_color_palette(self, industry: str) -> Dict[str, str]:
        """Suggest color palette."""
        return {
            "primary": "#0066CC",
            "secondary": "#FF9900",
            "accent": "#00CC66",
            "neutral": "#333333",
        }

    def _define_brand_personality(self, values: List[str], target_audience: str) -> str:
        """Define brand personality."""
        return "Innovative, reliable, and customer-focused"

    def _create_positioning_statement(self, brand_name: str, industry: str) -> str:
        """Create positioning statement."""
        return f"{brand_name} is the leading innovator in the {industry} space, providing cutting-edge solutions that empower our customers to achieve their goals."

    async def _generate_social_media(self, task: Task) -> Dict[str, Any]:
        """
        Generate social media content.

        Args:
            task: Task with social media parameters

        Returns:
            Social media content
        """
        platform = task.parameters.get("platform", "twitter")
        topic = task.parameters.get("topic", "Product Launch")
        tone = task.parameters.get("tone", "engaging")
        hashtags = task.parameters.get("hashtags", [])

        # Generate social media content
        social_content = self._create_social_media_content(
            platform=platform, topic=topic, tone=tone, hashtags=hashtags
        )

        content = CreativeContent(
            content_type=ContentType.SOCIAL_MEDIA,
            title=f"Social Media: {platform}",
            content=social_content,
            style=tone,
            mood="engaging",
            target_audience="followers",
            metadata={"platform": platform, "hashtags": hashtags},
        )

        return {
            "platform": platform,
            "content": content.content,
            "tone": tone,
            "hashtags": hashtags,
            "character_count": len(content.content),
            "metadata": content.metadata,
        }

    def _create_social_media_content(
        self, platform: str, topic: str, tone: str, hashtags: List[str]
    ) -> str:
        """Create social media content."""
        # Simplified social media generation (placeholder)

        if platform.lower() == "twitter":
            content = f"Excited to announce {topic}! 🚀 This is a game-changer. "
            if hashtags:
                content += " " + " ".join(f"#{tag}" for tag in hashtags)
            else:
                content += " #Innovation #Launch"
        elif platform.lower() == "linkedin":
            content = f"""
            
            We're thrilled to share {topic} with our network!
            
            This development represents a significant milestone in our journey to deliver exceptional value. We couldn't have done it without the support of our amazing team and community.
            
            {topic} #Innovation #Success
            
            """
        else:
            content = f"Check out {topic} - something exciting is happening!"

        return content.strip()

    async def _write_script(self, task: Task) -> Dict[str, Any]:
        """
        Write a script.

        Args:
            task: Task with script parameters

        Returns:
            Written script
        """
        script_type = task.parameters.get("script_type", "video")
        topic = task.parameters.get("topic", "Product Demo")
        duration = task.parameters.get("duration", "60 seconds")
        characters = task.parameters.get("characters", [])

        # Generate script
        script_content = self._create_script_content(
            script_type=script_type, topic=topic, duration=duration, characters=characters
        )

        content = CreativeContent(
            content_type=ContentType.SCRIPT,
            title=f"Script: {topic}",
            content=script_content,
            style="professional",
            mood="engaging",
            target_audience="general",
            metadata={"script_type": script_type, "duration": duration, "characters": characters},
        )

        return {
            "title": content.title,
            "content": content.content,
            "script_type": script_type,
            "duration": duration,
            "estimated_word_count": len(content.content.split()),
            "metadata": content.metadata,
        }

    def _create_script_content(
        self, script_type: str, topic: str, duration: str, characters: List[str]
    ) -> str:
        """Create script content."""
        # Simplified script generation (placeholder)

        script = f"""
        
        [SCENE START]
        
        [Opening shot: Professional setting]
        
        """

        if characters:
            for char in characters[:2]:  # Limit to 2 characters for simplicity
                script += f"{char}: Welcome to {topic}! Today we're going to explore something exciting.\n\n"
        else:
            script += "NARRATOR: Welcome to this exciting presentation about " + topic + "!\n\n"

        script += """
        
        [Visual: Product/service demonstration]
        
        Let's dive into the details and discover what makes this special.
        
        [Scene continues with explanation and examples]
        
        [SCENE END]
        
        """

        return script

    async def _describe_art(self, task: Task) -> Dict[str, Any]:
        """
        Describe art piece.

        Args:
            task: Task with art description parameters

        Returns:
            Art description
        """
        art_type = task.parameters.get("art_type", "painting")
        style = task.parameters.get("style", "abstract")
        mood = task.parameters.get("mood", "peaceful")
        elements = task.parameters.get("elements", [])

        # Generate art description
        art_description = self._create_art_description(
            art_type=art_type, style=style, mood=mood, elements=elements
        )

        content = CreativeContent(
            content_type=ContentType.ART_DESCRIPTION,
            title=f"Art Description: {art_type}",
            content=art_description,
            style=style,
            mood=mood,
            target_audience="art_enthusiasts",
            metadata={"art_type": art_type, "elements": elements},
        )

        return {
            "title": content.title,
            "content": content.content,
            "art_type": art_type,
            "style": style,
            "mood": mood,
            "metadata": content.metadata,
        }

    def _create_art_description(
        self, art_type: str, style: str, mood: str, elements: List[str]
    ) -> str:
        """Create art description."""
        # Simplified art description generation (placeholder)

        description = f"""
        
        This {art_type} piece exemplifies the {style} style, capturing a {mood} mood 
        through its thoughtful composition and expressive technique.
        
        """

        if elements:
            description += "Key elements include:\n\n"
            for element in elements:
                description += f"• {element}\n"

        description += f"""
        
        The artwork invites viewers to engage with its layered meaning and 
        emotional depth, creating a compelling visual experience that resonates 
        on multiple levels.
        
        """

        return description

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get MUSE agent statistics.

        Returns:
            Dictionary containing statistics
        """
        return {
            "content_types_supported": len(self.content_templates),
            "style_presets": len(self.style_presets),
            "specialization": "creative",
            "capabilities": self.capabilities.skills,
        }
