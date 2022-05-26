


class Forward:
    @iterative_migration()
    async def name_to_title(
            self, input_document, output_document
    ):
        output_document.title = input_document.title
        output_document.question = input_document.question


class Backward:
    ...
