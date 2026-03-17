from repositories import InMemoryRepository
from services.BusService import BusService


def main():
    print("Welcome to the event bus system!")

    in_memory_repository = InMemoryRepository()
    bus = BusService(repository=in_memory_repository)
    bus.publish()


if __name__ == "__main__":
    main()
