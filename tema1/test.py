import unittest
import main


class TestEncryptDecrypt(unittest.TestCase):
    def test_ECB(self):
        text = b'fisier1234textvulpeasarepestevizuina'
        key = b'acertainrandomkey'
        enc, chunk_size = main.ecb_encrypt(text, key, main.ECB_BLOCK_SIZE)
        self.assertEqual(main.ecb_decrypt(enc, key, chunk_size), text)

    def test_OFB(self):
        text = b'fisier1234textvulpeasarepestevizuina'
        key = b'acertainrandomkey'
        iv = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        enc, chunk_size = main.ofb_encrypt_decrypt(text, key, main.OFB_BLOCK_SIZE, iv)
        self.assertEqual(main.ofb_encrypt_decrypt(enc, key, chunk_size, iv)[0], text)


if __name__ == "__main__":
    unittest.main()