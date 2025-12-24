import logging
from typing import List, Optional
import meilisearch
from .config import settings
from .database import AsyncSessionFactory
from .models import Product
from sqlalchemy import select

logger = logging.getLogger(__name__)


class MeiliSearchClient:
    """Client for Meilisearch integration"""

    def __init__(self):
        """Initialize Meilisearch client"""
        meili_url = f"http://{settings.MEILI_HOST}:{settings.MEILI_PORT}"
        self.client = meilisearch.Client(
            meili_url,
            settings.MEILI_MASTER_KEY if settings.MEILI_MASTER_KEY else None
        )
        self.index_name = "products"
        self.index = None
        logger.info(f"Meilisearch client initialized at {meili_url}")

    async def init_index(self):
        """Initialize and configure the products index"""
        try:
            # Create or get index
            self.index = self.client.index(self.index_name)

            # Configure searchable attributes (fields to search in)
            self.index.update_searchable_attributes([
                'name',
                'description',
                'vendor',
                'vendor_code',
                'model'
            ])

            # Configure filterable attributes (for filtering results)
            self.index.update_filterable_attributes([
                'price',
                'availability',
                'vendor',
                'is_bestseller'
            ])

            # Configure sortable attributes
            self.index.update_sortable_attributes([
                'price'
            ])

            # Configure typo tolerance (enabled by default, but we ensure it's on)
            self.index.update_typo_tolerance({
                'enabled': True,
                'minWordSizeForTypos': {
                    'oneTypo': 5,
                    'twoTypos': 9
                }
            })

            logger.info(f"Index '{self.index_name}' configured successfully")

        except Exception as e:
            logger.error(f"Error initializing index: {e}")
            raise

    async def sync_products(self):
        """Sync all products from PostgreSQL to Meilisearch"""
        try:
            logger.info("Starting product synchronization...")

            # Fetch all products from database
            async with AsyncSessionFactory() as session:
                stmt = select(Product)
                result = await session.execute(stmt)
                products = result.scalars().all()

            if not products:
                logger.warning("No products found in database")
                return

            # Prepare documents for Meilisearch
            documents = []
            for product in products:
                doc = {
                    'id': product.id,
                    'name': product.name,
                    'vendor_code': product.vendor_code,
                    'price': float(product.price),
                    'vendor': product.vendor,
                    'model': product.model,
                    'description': product.description or '',
                    'availability': product.availability,
                    'is_bestseller': product.is_bestseller
                }
                documents.append(doc)

            # Add documents to Meilisearch
            if self.index is None:
                await self.init_index()

            task = self.index.add_documents(documents)
            logger.info(f"Synced {len(documents)} products to Meilisearch. Task UID: {task.task_uid}")

            # Wait for the task to complete
            self.client.wait_for_task(task.task_uid)
            logger.info("Product synchronization completed successfully")

        except Exception as e:
            logger.error(f"Error syncing products: {e}")
            raise

    def search_products(self, query: str, limit: int = 5) -> List[int]:
        """
        Search products and return list of product IDs

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of product IDs
        """
        try:
            if self.index is None:
                logger.error("Index not initialized")
                return []

            # Perform search
            results = self.index.search(
                query,
                {
                    'limit': limit,
                    'attributesToRetrieve': ['id']
                }
            )

            # Extract product IDs
            product_ids = [hit['id'] for hit in results['hits']]
            logger.info(f"Search query '{query}' returned {len(product_ids)} results")

            return product_ids

        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []

    async def health_check(self) -> bool:
        """Check if Meilisearch is healthy"""
        try:
            health = self.client.health()
            return health.get('status') == 'available'
        except Exception as e:
            logger.error(f"Meilisearch health check failed: {e}")
            return False


# Global instance
meili_client: Optional[MeiliSearchClient] = None


async def get_meili_client() -> MeiliSearchClient:
    """Get or create global Meilisearch client instance"""
    global meili_client
    if meili_client is None:
        meili_client = MeiliSearchClient()
        await meili_client.init_index()
    return meili_client
