"""Transcript processing - extract sentences, words, and timing information."""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Word:
    """Represents a single word with timing information."""

    text: str
    start: float
    end: float
    confidence: float = 0.95


@dataclass
class Sentence:
    """Represents a sentence with timing and component words."""

    text: str
    start: float
    end: float
    words: List[Word]
    confidence: float = 0.95


class TranscriptProcessor:
    """Process Whisper output into structured sentences and words with timing."""

    @staticmethod
    def extract_words_from_segments(segments: List[Dict]) -> List[Word]:
        """
        Extract word-level information from Whisper segments.

        Args:
            segments: List of segment dictionaries from Whisper output

        Returns:
            List of Word objects with timing information
        """
        words = []

        for segment in segments:
            # Whisper provides 'words' in some outputs, fall back to splitting text
            if segment.get("words"):
                for word_item in segment["words"]:
                    words.append(
                        Word(
                            text=word_item.get("word", "").strip(),
                            start=word_item.get("start", 0.0),
                            end=word_item.get("end", 0.0),
                            confidence=word_item.get("probability", 0.95),
                        )
                    )
            else:
                # Fall back to simple word splitting if word-level timing not available
                text = segment.get("text", "").strip()
                start = segment.get("start", 0.0)
                end = segment.get("end", 0.0)

                if text:
                    word_tokens = text.split()
                    if word_tokens:
                        # Distribute time evenly across words
                        word_duration = (end - start) / len(word_tokens)
                        for i, word in enumerate(word_tokens):
                            words.append(
                                Word(
                                    text=word,
                                    start=start + (i * word_duration),
                                    end=start + ((i + 1) * word_duration),
                                    confidence=segment.get("confidence", 0.95),
                                )
                            )

        return words

    @staticmethod
    def group_words_into_sentences(
        words: List[Word],
        min_sentence_length: int = 3,
        max_sentence_length: int = 40,
        max_pause: float = 1.5,
    ) -> List[Sentence]:
        """
        Group words into sentences based on natural pauses and punctuation.

        Args:
            words: List of Word objects
            min_sentence_length: Minimum words before a pause can end a sentence
            max_sentence_length: Maximum words per sentence when no punctuation is found
            max_pause: Silence (seconds) before the next word that ends a sentence

        Returns:
            List of Sentence objects
        """
        if not words:
            return []

        sentences = []
        current_sentence_words: List[Word] = []

        def flush() -> None:
            sentences.append(
                Sentence(
                    text=" ".join(w.text for w in current_sentence_words),
                    start=current_sentence_words[0].start,
                    end=current_sentence_words[-1].end,
                    words=list(current_sentence_words),
                    confidence=sum(w.confidence for w in current_sentence_words)
                    / len(current_sentence_words),
                )
            )
            current_sentence_words.clear()

        for i, word in enumerate(words):
            current_sentence_words.append(word)
            next_word = words[i + 1] if i + 1 < len(words) else None

            is_end_of_sentence = word.text.rstrip("\"')").endswith((".", "!", "?"))
            long_pause = (
                next_word is not None
                and next_word.start - word.end >= max_pause
                and len(current_sentence_words) >= min_sentence_length
            )
            too_long = len(current_sentence_words) >= max_sentence_length

            if is_end_of_sentence or long_pause or too_long:
                flush()

        # Add remaining words as final sentence
        if current_sentence_words:
            flush()

        return sentences

    @staticmethod
    def process_whisper_output(result: Dict) -> Tuple[str, List[Sentence], List[Word]]:
        """
        Process complete Whisper transcription output.

        Args:
            result: Complete dictionary returned from Whisper model.transcribe()

        Returns:
            Tuple of (full_text, sentences, words)
        """
        # Extract text and segments
        full_text = result.get("text", "").strip()
        segments = result.get("segments", [])
        language = result.get("language", "en")

        logger.info(f"Processing Whisper output: {len(segments)} segments, language={language}")

        # Extract words from segments
        words = TranscriptProcessor.extract_words_from_segments(segments)
        logger.info(f"Extracted {len(words)} words with timing information")

        # Group into sentences
        sentences = TranscriptProcessor.group_words_into_sentences(words)
        logger.info(f"Grouped into {len(sentences)} sentences")

        return full_text, sentences, words

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize transcript text."""
        # Remove extra whitespace
        text = " ".join(text.split())
        # Normalize quotes
        text = text.replace(""", '"').replace(""", '"')
        text = text.replace("'", "'")
        return text

    @staticmethod
    def estimate_reading_time(word_count: int, wpm: int = 200) -> int:
        """
        Estimate reading time in seconds.

        Args:
            word_count: Number of words
            wpm: Words per minute (default 200)

        Returns:
            Estimated reading time in seconds
        """
        return int((word_count / wpm) * 60)
