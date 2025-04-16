from mm.book_utils import BookUtils


class TestBookUtils:

    def test_book_utils(self):
        book_utils = BookUtils(
            "tests/book/text",
            "target/eco_estrellas",
            "El Eco de las Estrellas",
            "Claude",
            "tests/book/book-cover.jpg",
            "es",
            "mobi"
        )
        actual = book_utils.create_book()
        expected = "target/eco_estrellas/El_Eco_de_las_Estrellas.mobi"
        assert actual == expected