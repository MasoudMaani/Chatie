import random
import re
from typing import List, Tuple
from enum import Enum

class Phoneme(Enum):
    """Phoneme types for pronounceability"""
    VOWEL = "vowel"
    CONSONANT = "consonant"

class WordGenerator:
    """Generates pronounceable synthetic English words"""
    
    # Define phoneme inventory
    VOWELS = set('aeiou')
    CONSONANTS = set('bcdfghjklmnpqrstvwxyz')

    # Common onset clusters (consonant groups at word start)
    ONSET_CLUSTERS = {
        'bl', 'br', 'ch', 'cl', 'cr', 'dr', 'dw', 'fl', 'fr', 'gh', 'gl', 'gr',
        'kn', 'ph', 'pl', 'pr', 'qu', 'sc', 'sh', 'sk', 'sl', 'sm', 'sn', 'sp',
        'st', 'sw', 'th', 'tr', 'tw', 'wh', 'wr'
    }
    
    # Common coda clusters (consonant groups at word end)
    CODA_CLUSTERS = {
        'ch', 'ck', 'ct', 'ft', 'ld', 'lf', 'lk', 'lm', 'ln', 'lp', 'ls', 'lt',
        'mp', 'nd', 'ng', 'nk', 'nt', 'pt', 'rd', 'rk', 'rm', 'rn', 'rp', 'rt',
        'sh', 'st', 'th', 'xt'
    }

    DIPHTHONGS = {
        'ai', 'au', 'ea', 'ei', 'eu', 'oa', 'oi', 'ou'
    }

    # Constraints
    MIN_LENGTH = 2
    MAX_LENGTH = 15
    
    def __init__(self, seed: int = None):
        """Initialize the word generator with optional seed for reproducibility"""
        if seed is not None:
            random.seed(seed)
    
    @staticmethod
    def _get_phoneme_type(char: str) -> Phoneme:
        """Determine if a character is a vowel or consonant"""
        if char.lower() in WordGenerator.VOWELS:
            return Phoneme.VOWEL
        elif char.lower() in WordGenerator.CONSONANTS:
            return Phoneme.CONSONANT
        else:
            raise ValueError(f"Invalid character: {char}")
    
    @staticmethod
    def _is_valid_sequence(sequence: str) -> bool:
        """
        Check if a sequence follows pronounceability rules:
        - No more than 2 consecutive consonants (except in clusters)
        - No more than 2 consecutive vowels (excluding diphthongs)
        - Must follow phonotactic patterns
        """
        i = 0
        while i < len(sequence):
            # Check if this is a diphthong
            if i + 1 < len(sequence) and sequence[i:i+2] in WordGenerator.DIPHTHONGS:
                i += 2
                continue
            
            # Check for invalid consonant clusters
            if (i + 1 < len(sequence) and 
                WordGenerator._get_phoneme_type(sequence[i]) == Phoneme.CONSONANT and
                WordGenerator._get_phoneme_type(sequence[i+1]) == Phoneme.CONSONANT):
                two_char = sequence[i:i+2]
                if two_char not in WordGenerator.ONSET_CLUSTERS and two_char not in WordGenerator.CODA_CLUSTERS:
                    return False

            # Check for too many consecutive vowels (max 2, but diphthongs are already handled)
            if WordGenerator._get_phoneme_type(sequence[i]) == Phoneme.VOWEL:
                consecutive_vowels = 1
                j = i + 1
                while j < len(sequence) and WordGenerator._get_phoneme_type(sequence[j]) == Phoneme.VOWEL:
                    # Skip diphthongs
                    if j + 1 < len(sequence) and sequence[j:j+2] in WordGenerator.DIPHTHONGS:
                        j += 2
                        break
                    consecutive_vowels += 1
                    j += 1

                if consecutive_vowels > 2:
                    return False

            i += 1

        return True

    
    def generate_syllable(self) -> str:
        """Generate a single pronounceable syllable (CV, CVC, V, VC, CCV, etc.)"""
        structures = [
            'V',      # vowel
            'CV',     # consonant-vowel
            'CVC',    # consonant-vowel-consonant
            'CCV',    # consonant cluster-vowel
            'CCVC',   # consonant cluster-vowel-consonant
            'VC',     # vowel-consonant
        ]
        
        structure = random.choice(structures)
        syllable = ""
        
        i = 0
        while i < len(structure):
            if structure[i] == 'C':
                # Check if next char is also C (cluster)
                if i + 1 < len(structure) and structure[i+1] == 'C':
                    # Use onset or coda cluster
                    clusters = list(self.ONSET_CLUSTERS if not syllable else self.CODA_CLUSTERS)
                    if clusters:
                        syllable += random.choice(clusters)
                        i += 2
                        continue
                
                # Single consonant
                syllable += random.choice(list(self.CONSONANTS))
                i += 1
            elif structure[i] == 'V':
                # Vowel (sometimes diphthong)
                if random.random() < 0.2 and syllable:  # 20% chance for diphthong
                    vowel_pair = random.choice(['ai', 'au', 'ea', 'ei', 'eu', 'oa', 'oi', 'ou'])
                    syllable += vowel_pair
                else:
                    syllable += random.choice(list(self.VOWELS))
                i += 1
            else:
                i += 1
        
        return syllable
    
    def generate_word(self, target_length: int = None) -> str:
        """
        Generate a pronounceable word within length constraints.
        
        Args:
            target_length: Desired length (2-15). If None, random within range.
        
        Returns:
            A pronounceable synthetic word
        """
        if target_length is None:
            target_length = random.randint(self.MIN_LENGTH, self.MAX_LENGTH)
        else:
            if not (self.MIN_LENGTH <= target_length <= self.MAX_LENGTH):
                raise ValueError(f"Length must be between {self.MIN_LENGTH} and {self.MAX_LENGTH}")
        
        max_attempts = 100
        attempts = 0
        
        while attempts < max_attempts:
            word = ""
            
            # Generate syllables until we reach target length
            while len(word) < target_length:
                syllable = self.generate_syllable()
                if len(word) + len(syllable) <= target_length:
                    word += syllable
                else:
                    break
            
            # Ensure word meets minimum length
            if len(word) >= self.MIN_LENGTH and self._is_valid_sequence(word):
                return word
            
            attempts += 1
        
        # Fallback: return simple valid word
        return self.generate_simple_word(target_length)
    
    def generate_simple_word(self, length: int) -> str:
        """Fallback method to generate a simple, guaranteed valid word"""
        word = ""
        is_vowel_turn = random.choice([True, False])
        
        while len(word) < length:
            if is_vowel_turn:
                word += random.choice(list(self.VOWELS))
            else:
                word += random.choice(list(self.CONSONANTS))
            is_vowel_turn = not is_vowel_turn
        
        return word[:length]
    
    def generate_batch(self, count: int, length_range: Tuple[int, int] = None) -> List[str]:
        """
        Generate multiple words.
        
        Args:
            count: Number of words to generate
            length_range: Tuple of (min_length, max_length). Defaults to (2, 15)
        
        Returns:
            List of pronounceable words
        """
        if length_range is None:
            length_range = (self.MIN_LENGTH, self.MAX_LENGTH)
        
        words = []
        for _ in range(count):
            length = random.randint(length_range[0], length_range[1])
            words.append(self.generate_word(length))
        
        return words


# ============================================================================
# UNIT TESTS
# ============================================================================

class TestWordGenerator:
    """Unit tests for WordGenerator"""
    
    def __init__(self):
        self.generator = WordGenerator(seed=42)
        self.passed = 0
        self.failed = 0
    
    def assert_true(self, condition: bool, message: str):
        """Assert that a condition is true"""
        if condition:
            self.passed += 1
            print(f"✓ {message}")
        else:
            self.failed += 1
            print(f"✗ {message}")
    
    def assert_equal(self, actual, expected, message: str):
        """Assert that two values are equal"""
        if actual == expected:
            self.passed += 1
            print(f"✓ {message}")
        else:
            self.failed += 1
            print(f"✗ {message} (expected {expected}, got {actual})")
    
    def assert_in_range(self, value: int, min_val: int, max_val: int, message: str):
        """Assert that a value is within a range"""
        if min_val <= value <= max_val:
            self.passed += 1
            print(f"✓ {message}")
        else:
            self.failed += 1
            print(f"✗ {message} (expected {min_val}-{max_val}, got {value})")
    
    def test_length_bounds(self):
        """Test that generated words respect length constraints"""
        print("\n--- Testing Length Bounds ---")
        
        for _ in range(10):
            word = self.generator.generate_word()
            self.assert_in_range(
                len(word),
                WordGenerator.MIN_LENGTH,
                WordGenerator.MAX_LENGTH,
                f"Word '{word}' length {len(word)} within bounds"
            )
    
    def test_specific_length(self):
        """Test that words can be generated at specific lengths"""
        print("\n--- Testing Specific Length Generation ---")
        
        for target_length in [2, 5, 10, 15]:
            word = self.generator.generate_word(target_length)
            self.assert_equal(
                len(word),
                target_length,
                f"Generated word of length {target_length}: '{word}'"
            )
    
    def test_pronounceability(self):
        """Test that generated words follow pronounceability rules"""
        print("\n--- Testing Pronounceability Rules ---")
        
        for _ in range(20):
            word = self.generator.generate_word()
            is_valid = self.generator._is_valid_sequence(word)
            self.assert_true(
                is_valid,
                f"Word '{word}' follows pronounceability rules"
            )
    
    def test_no_invalid_clusters(self):
        """Test that no invalid consonant clusters exist"""
        print("\n--- Testing Invalid Cluster Detection ---")
        
        test_words = [
            ("hello", True),      # Valid
            ("strength", True),   # Valid (str cluster)
            ("blue", True),       # Valid (bl cluster)
            ("bzzz", False),      # Invalid (invalid cluster)
        ]
        
        for word, should_be_valid in test_words:
            is_valid = self.generator._is_valid_sequence(word)
            self.assert_equal(
                is_valid,
                should_be_valid,
                f"Word '{word}' validity check: {is_valid}"
            )
    
    def test_batch_generation(self):
        """Test batch word generation"""
        print("\n--- Testing Batch Generation ---")
        
        batch_size = 50
        words = self.generator.generate_batch(batch_size)
        
        self.assert_equal(
            len(words),
            batch_size,
            f"Generated batch of {batch_size} words"
        )
        
        all_valid = all(self.generator._is_valid_sequence(w) for w in words)
        self.assert_true(
            all_valid,
            "All words in batch are valid"
        )
    
    def test_no_consecutive_vowels_exceeding_limit(self):
        """Test that no word has more than 2 consecutive vowels"""
        print("\n--- Testing Consecutive Vowel Limit ---")
        
        for _ in range(20):
            word = self.generator.generate_word()
            vowels = [c for c in word if c in WordGenerator.VOWELS]
            
            # Check manually
            max_consecutive = 0
            current = 0
            for c in word:
                if c in WordGenerator.VOWELS:
                    current += 1
                    max_consecutive = max(max_consecutive, current)
                else:
                    current = 0
            
            self.assert_true(
                max_consecutive <= 2,
                f"Word '{word}' has max {max_consecutive} consecutive vowels (≤ 2)"
            )
    
    def test_invalid_length_raises_error(self):
        """Test that invalid lengths raise appropriate errors"""
        print("\n--- Testing Invalid Length Handling ---")
        
        try:
            self.generator.generate_word(1)  # Too short
            self.assert_true(False, "Should raise error for length < 2")
        except ValueError:
            self.assert_true(True, "Raises error for length < 2")
        
        try:
            self.generator.generate_word(16)  # Too long
            self.assert_true(False, "Should raise error for length > 15")
        except ValueError:
            self.assert_true(True, "Raises error for length > 15")
    
    def run_all_tests(self):
        """Run all tests and print summary"""
        print("=" * 60)
        print("WORD GENERATOR TEST SUITE")
        print("=" * 60)
        
        self.test_length_bounds()
        self.test_specific_length()
        self.test_pronounceability()
        self.test_no_invalid_clusters()
        self.test_batch_generation()
        self.test_no_consecutive_vowels_exceeding_limit()
        self.test_invalid_length_raises_error()
        
        print("\n" + "=" * 60)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print("=" * 60)
        
        return self.failed == 0


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Run tests
    tester = TestWordGenerator()
    tester.run_all_tests()
    
    # Generate some example words
    print("\n\nSample Generated Words:")
    print("=" * 60)
    gen = WordGenerator(seed=123)
    
    print("\nRandom lengths:")
    for _ in range(10):
        word = gen.generate_word()
        print(f"  {word} (length: {len(word)})")
    
    print("\nSpecific lengths:")
    for length in [2, 3, 5, 7, 10, 15]:
        words = [gen.generate_word(length) for _ in range(3)]
        print(f"  Length {length:2d}: {', '.join(words)}")
    
    print("\nBatch of 20 random words:")
    batch = gen.generate_batch(20)
    print(f"  {', '.join(batch)}")
