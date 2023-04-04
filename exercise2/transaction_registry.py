from simple_cryptography import hash, PublicKey, verify_signature
from typing import Optional, List
import copy


class Transaction:
    """
    Transakcja zawiera:
    - odbiorcę transakcji (klucz publiczny)
    - hash poprzedniej transakcji
    """

    recipient: PublicKey
    previous_tx_hash: bytes
    tx_hash: bytes

    def __init__(self, recipient: PublicKey, previous_tx_hash: bytes):
        self.recipient = recipient
        self.previous_tx_hash = previous_tx_hash

        self.tx_hash = hash(self.recipient.to_bytes() + self.previous_tx_hash)

    def __repr__(self):
        return f"Tx(recipient: {self.recipient.to_bytes()[-6:]}.., prev_hash: {self.previous_tx_hash[:6]}..)"


class SignedTransaction(Transaction):
    """
    Podpisana transakcja zawiera dodatkowo:
    - Podpis transakcji, utworzony przy pomocy klucza prywatnego poprzedniego właściciela transakcji.
    """

    signature: bytes

    def __init__(self, recipient: PublicKey, previous_tx_hash: bytes, signature: bytes):
        super().__init__(recipient, previous_tx_hash)
        self.signature = signature

    @staticmethod
    def from_transaction(transaction: Transaction, signature: bytes):
        return SignedTransaction(
            transaction.recipient, transaction.previous_tx_hash, signature
        )

    def __repr__(self):
        return f"SignedTx(recipient: {self.recipient.to_bytes()[-6:]}.., prev_hash: {self.previous_tx_hash[:6]}.., signature: {self.signature[:6]})"


class TransactionRegistry:
    """
    Klasa reprezentująca publiczny rejestr transakcji. Odpowiada za przyjmowanie nowych transakcji i ich
    przechowywanie.
    """

    transactions: List[Transaction]

    def __init__(self, initial_transactions: List[Transaction]):
        self.transactions = copy.copy(initial_transactions)

    def get_transaction(self, tx_hash: bytes) -> Optional[Transaction]:
        """
        TODO: Znajdź transakcję z podanym tx_hash.
        Jeśli w liście transakcji istnieje transakcja z podanym tx_hash, zwróć ją,
        w przeciwnym przypadku zwróć None.
        """
        for tx in self.transactions:
            if tx.tx_hash == tx_hash:
                return tx
        return None

    def is_transaction_available(self, tx_hash: bytes) -> bool:
        """
        TODO: Sprawdź czy transakcja o podanym hashu istnieje i nie została wykorzystana.
        1.  Sprawdź czy istnieje transakcja o podanym tx_hash, jeśli nie, zwróć False.
        2.  Przeszukaj listę transakcji w poszukiwaniu transakcji, dla której pole
            previous_tx_hash jest równe podanemu w argumencie tx_hash. Jeśli taka transakcja
            istnieje, oznacza to że transakcja o hashu tx_hash zostala już wykorzystana. Zwróć
            False.
        3. Jeśli w poprzednich krokach nic nie zwrócono - transakcja jest dostępna, zwróć True.
        """
        if self.get_transaction(tx_hash) is None:
            return False

        for tx in self.transactions:
            if tx.previous_tx_hash == tx_hash:
                return False
        return True

    def verify_transaction_signature(self, transaction: SignedTransaction) -> bool:
        """
        TODO: Zweryfikuj podpis nowej transakcji.
        1.  Znajdź poprzednią transakcję względem transaction, pole previous_tx_hash z argumentu transaction.
            Jeśli nie istnieje, zwróć False.
        2.  Sprawdź czy dana transakcja została podpisana przez właściciela (klucz publiczny) poprzedniej transakcji.
            Wykorzystaj do tego metodę verify_signature z simple_cryptography.
        Przypomnienie: podpisywany jest hash transakcji.
        """
        previous_transaction = self.get_transaction(transaction.previous_tx_hash)

        if previous_transaction is None:
            return False

        return verify_signature(
            previous_transaction.recipient, transaction.signature, transaction.tx_hash
        )

    def add_transaction(self, transaction: SignedTransaction) -> bool:
        """
        TODO: Dodaj nową transakcję do listy transakcji.
        Przed dodaniem upewnij się, że:
        1.  Poprzednia transakcja jest niewykorzystana.
        2.  Podpis transakcji jest prawidlowy.
        Wykorzystaj do tego dwie metody powyżej.
        Zwróć True jeśli dodanie transakcji przebiegło pomyślnie, False w przeciwnym wypadku.
        """
        if not self.verify_transaction_signature(transaction):
            return False

        if not self.is_transaction_available(transaction.previous_tx_hash):
            return False

        self.transactions.append(transaction)
        return True
