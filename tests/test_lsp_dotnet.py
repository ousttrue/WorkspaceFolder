import unittest
import asyncio
import logging
import pathlib
from workspacefolder import lsp
from workspacefolder.lsp import workspaceinfo
logger = logging.getLogger(__name__)


class LspTests(unittest.TestCase):
    def test_omni(self):
        async def run():
            samples = pathlib.Path(
                __file__).resolve().parent.parent / 'samples'
            path = samples / 'dotnetcore/Program.cs'
            self.assertTrue(path.exists())

            # proj = workspaceinfo.find_to_ancestors(path, "*.csproj")
            # self.assertTrue(proj)
            #
            # info = workspaceinfo.get_workspaceinfo(path)
            # self.assertTrue(info)

            text = path.read_text('utf-8')

            lspi = lsp.LspInterface()

            document = lspi.get_or_create_document(path)
            self.assertTrue(document)

            # wait diagnostics
            await asyncio.sleep(2)

            await document.notify_open(text)

            # wait diagnostics
            await asyncio.sleep(1)

            await document.notify_change(text)

            await document.request_highlight(0, 0)
            await document.request_definition(0, 0)
            await document.request_completion(44 - 1, 16 - 1)
            await document.request_hover(0, 0)
            await document.request_references(0, 0)

            await asyncio.sleep(2)

            lspi.shutdown()
            logger.debug('done')

        asyncio.run(run())


if __name__ == '__main__':
    f = '%(asctime)s[%(levelname)s][%(name)s.%(funcName)s] %(message)s'
    logging.basicConfig(level=logging.DEBUG, datefmt='%H:%M:%S', format=f)

    unittest.main()
