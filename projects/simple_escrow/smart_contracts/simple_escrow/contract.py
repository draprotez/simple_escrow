from algopy import ARC4Contract, subroutine, Global, UInt64, itxn, Txn
from algopy.arc4 import abimethod


class SimpleEscrow(ARC4Contract):
    """
    Smart Contract Simple Escrow (versi sederhana)
    Pembeli mengirim dana, lalu dana bisa dilepaskan ke penjual
    """

    def __init__(self) -> None:
        self.buyer = Txn.sender
        self.seller = Global.creator_address
        self.amount = UInt64(0)
        self.is_funded = UInt64(0)

    @abimethod
    def fund(self) -> UInt64:
        """
        Dipanggil oleh PEMBELI untuk mendanai escrow
        """
        assert Txn.sender == self.buyer, "Hanya pembeli"
        assert self.is_funded == UInt64(0), "Sudah didanai"
        assert Txn.amount > UInt64(0), "Jumlah harus > 0"

        self.amount = Txn.amount
        self.is_funded = UInt64(1)

        return self.amount

    @abimethod
    def release(self) -> UInt64:
        """
        Dipanggil oleh PEMBELI untuk melepaskan dana ke penjual
        """
        assert Txn.sender == self.buyer, "Hanya pembeli"
        assert self.is_funded == UInt64(1), "Belum didanai"

        itxn.Payment(
            receiver=self.seller,
            amount=self.amount,
            fee=0
        ).submit()

        self.amount = UInt64(0)
        self.is_funded = UInt64(0)

        return UInt64(1)

    @abimethod
    def refund(self) -> UInt64:
        """
        Dipanggil oleh PENJUAL untuk mengembalikan dana ke pembeli
        """
        assert Txn.sender == self.seller, "Hanya penjual"
        assert self.is_funded == UInt64(1), "Belum didanai"

        itxn.Payment(
            receiver=self.buyer,
            amount=self.amount,
            fee=0
        ).submit()

        self.amount = UInt64(0)
        self.is_funded = UInt64(0)

        return UInt64(1)

    @subroutine
    def get_status(self) -> UInt64:
        """
        Cek apakah escrow sedang aktif
        """
        return self.is_funded
