from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hash:
    """Esta clase realiza el hash y verificacion de un password."""

    def bcrypt(self, password: str) -> str:
        """Hashea un password.

        Args:
            self (Self): self
            password (str): Cadena de texto para hashearla

        Returns:
            str: un hash en string
        """
        return pwd_context.hash(password)

    def verify(self, hashed_password, plain_password: str) -> bool:
        """Verificar Hash.

        Args:
            self (Self): self
            hashed_password (bool): pasa un hash
            plain_password (str): pasa un password en texto plano

        Returns:
            bool: Regresa un booleando indicando si coinciden los hashes.
        """
        return pwd_context.verify(plain_password, hashed_password)
