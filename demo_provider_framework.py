import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.research.providers.registry import ProviderRegistry
from agents.research.providers.adapters import GitHubProviderAdapter, LocalDocumentProviderAdapter, RSSProviderAdapter


async def main() -> None:
    registry = ProviderRegistry()
    registry.register(LocalDocumentProviderAdapter(root=ROOT))
    registry.register(RSSProviderAdapter(feed_path=ROOT / 'docs' / 'fixtures' / 'titan-news.xml'))
    registry.register(GitHubProviderAdapter(repo_root=ROOT))
    response = await registry.query('provider framework')
    print(response.summary)
    for item in response.results[:5]:
        print(item.provider_name, '=>', item.title, '|', item.confidence)


asyncio.run(main())
