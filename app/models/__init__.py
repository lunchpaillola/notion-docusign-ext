# This will be populated when Prisma generates the client
from .prisma import PrismaClient

db = PrismaClient()

__all__ = ['db'] 