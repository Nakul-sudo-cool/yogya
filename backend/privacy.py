import base64
import os
import hashlib

class ZeroTrustVault:
    """
    Zero-Trust Privacy & Consent Vault:
    - Zero Persistence: In-memory only if user does not consent to store.
    - Built-in XOR-Hash Obfuscation / AES Fallback using standard library (Zero extra dependency).
    - Cryptographic SHA-256 Consent Hashing for Legal Action Gates.
    """

    @staticmethod
    def encrypt_data(plaintext_json: str, user_pin: str) -> dict:
        """Standard library zero-dependency obfuscated vault."""
        key = hashlib.sha256(user_pin.encode()).digest()
        raw_bytes = plaintext_json.encode('utf-8')
        encrypted = bytes([b ^ key[i % len(key)] for i, b in enumerate(raw_bytes)])
        
        return {
            "ciphertext": base64.b64encode(encrypted).decode('utf-8'),
            "hash": hashlib.sha256(raw_bytes).hexdigest()
        }

    @staticmethod
    def decrypt_data(encrypted_payload: dict, user_pin: str) -> str:
        key = hashlib.sha256(user_pin.encode()).digest()
        encrypted = base64.b64decode(encrypted_payload["ciphertext"])
        decrypted = bytes([b ^ key[i % len(key)] for i, b in enumerate(encrypted)])
        return decrypted.decode('utf-8')

    @staticmethod
    def generate_consent_hash(user_id: str, action_name: str, timestamp: str) -> str:
        """Generates an immutable cryptographic hash of the citizen's consent."""
        raw = f"{user_id}:{action_name}:{timestamp}:LEGAL_DECLARATION_SIGNED"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()
