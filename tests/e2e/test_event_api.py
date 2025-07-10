import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
import pytz


class TestEventAPIE2E:
    """End-to-end tests for Event API endpoints"""

    @pytest.mark.asyncio
    async def test_create_event_success(self, async_client: AsyncClient):
        """Test successful event creation via API"""
        # Arrange
        event_data = {
            "name": "Tech Conference 2024",
            "location": "Convention Center, Mumbai",
            "start_time": (datetime.now() + timedelta(days=30)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=30, hours=8)).isoformat(),
            "max_capacity": 100,
        }

        # Act
        response = await async_client.post("/events/", json=event_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == event_data["name"]
        assert data["location"] == event_data["location"]
        assert data["max_capacity"] == event_data["max_capacity"]
        assert "id" in data
        assert data["current_attendee_count"] == 0
        assert data["available_spots"] == 100
        assert data["is_full"] is False

    @pytest.mark.asyncio
    async def test_create_event_validation_error(self, async_client: AsyncClient):
        """Test event creation with validation errors"""
        # Arrange
        event_data = {
            "name": "",  # Empty name should fail
            "location": "Convention Center, Mumbai",
            "start_time": (datetime.now() + timedelta(days=30)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=30, hours=8)).isoformat(),
            "max_capacity": 100,
        }

        # Act
        response = await async_client.post("/events/", json=event_data)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_create_event_past_date_error(self, async_client: AsyncClient):
        """Test event creation with past start date"""
        # Arrange
        event_data = {
            "name": "Tech Conference 2024",
            "location": "Convention Center, Mumbai",
            "start_time": (datetime.now() - timedelta(days=1)).isoformat(),  # Past date
            "end_time": (datetime.now() + timedelta(hours=8)).isoformat(),
            "max_capacity": 100,
        }

        # Act
        response = await async_client.post("/events/", json=event_data)

        # Assert
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_events_empty_list(self, async_client: AsyncClient):
        """Test getting events when none exist"""
        # Act
        response = await async_client.get("/events/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_get_events_with_pagination(self, async_client: AsyncClient):
        """Test getting events with pagination parameters"""
        # Arrange - Create a few events first
        events_data = [
            {
                "name": f"Event {i}",
                "location": f"Location {i}",
                "start_time": (datetime.now() + timedelta(days=i)).isoformat(),
                "end_time": (datetime.now() + timedelta(days=i, hours=2)).isoformat(),
                "max_capacity": 50,
            }
            for i in range(1, 4)
        ]

        # Create events
        for event_data in events_data:
            await async_client.post("/events/", json=event_data)

        # Act - Test pagination
        response = await async_client.get("/events/?limit=2&offset=0")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 2

    @pytest.mark.asyncio
    async def test_register_attendee_success(self, async_client: AsyncClient):
        """Test successful attendee registration"""
        # Arrange - Create an event first
        event_data = {
            "name": "Tech Conference 2024",
            "location": "Convention Center, Mumbai",
            "start_time": (datetime.now() + timedelta(days=30)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=30, hours=8)).isoformat(),
            "max_capacity": 100,
        }

        event_response = await async_client.post("/events/", json=event_data)
        event_id = event_response.json()["id"]

        attendee_data = {"name": "John Doe", "email": "john.doe@example.com"}

        # Act
        response = await async_client.post(
            f"/events/{event_id}/register", json=attendee_data
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == attendee_data["name"]
        assert data["email"] == attendee_data["email"]
        assert data["event_id"] == event_id
        assert "id" in data
        assert "registered_at" in data

    @pytest.mark.asyncio
    async def test_register_attendee_event_not_found(self, async_client: AsyncClient):
        """Test registering attendee for non-existent event"""
        # Arrange
        attendee_data = {"name": "John Doe", "email": "john.doe@example.com"}

        # Act
        response = await async_client.post("/events/999/register", json=attendee_data)

        # Assert
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_register_attendee_duplicate_registration(
        self, async_client: AsyncClient
    ):
        """Test duplicate attendee registration"""
        # Arrange - Create an event first
        event_data = {
            "name": "Tech Conference 2024",
            "location": "Convention Center, Mumbai",
            "start_time": (datetime.now() + timedelta(days=30)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=30, hours=8)).isoformat(),
            "max_capacity": 100,
        }

        event_response = await async_client.post("/events/", json=event_data)
        event_id = event_response.json()["id"]

        attendee_data = {"name": "John Doe", "email": "john.doe@example.com"}

        # Register attendee first time
        await async_client.post(f"/events/{event_id}/register", json=attendee_data)

        # Act - Try to register same attendee again
        response = await async_client.post(
            f"/events/{event_id}/register", json=attendee_data
        )

        # Assert
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_register_attendee_capacity_exceeded(self, async_client: AsyncClient):
        """Test attendee registration when event is at capacity"""
        # Arrange - Create an event with capacity of 1
        event_data = {
            "name": "Small Event",
            "location": "Small Venue",
            "start_time": (datetime.now() + timedelta(days=30)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=30, hours=2)).isoformat(),
            "max_capacity": 1,
        }

        event_response = await async_client.post("/events/", json=event_data)
        event_id = event_response.json()["id"]

        # Register first attendee
        attendee1_data = {"name": "John Doe", "email": "john.doe@example.com"}
        await async_client.post(f"/events/{event_id}/register", json=attendee1_data)

        # Act - Try to register second attendee
        attendee2_data = {"name": "Jane Smith", "email": "jane.smith@example.com"}
        response = await async_client.post(
            f"/events/{event_id}/register", json=attendee2_data
        )

        # Assert
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_get_event_attendees_success(self, async_client: AsyncClient):
        """Test successful retrieval of event attendees"""
        # Arrange - Create an event and register attendees
        event_data = {
            "name": "Tech Conference 2024",
            "location": "Convention Center, Mumbai",
            "start_time": (datetime.now() + timedelta(days=30)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=30, hours=8)).isoformat(),
            "max_capacity": 100,
        }

        event_response = await async_client.post("/events/", json=event_data)
        event_id = event_response.json()["id"]

        # Register multiple attendees
        attendees_data = [
            {"name": "John Doe", "email": "john.doe@example.com"},
            {"name": "Jane Smith", "email": "jane.smith@example.com"},
            {"name": "Bob Johnson", "email": "bob.johnson@example.com"},
        ]

        for attendee_data in attendees_data:
            await async_client.post(f"/events/{event_id}/register", json=attendee_data)

        # Act
        response = await async_client.get(f"/events/{event_id}/attendees")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "attendees" in data
        assert "total_count" in data
        assert "limit" in data
        assert "offset" in data
        assert "has_more" in data
        assert len(data["attendees"]) == 3
        assert data["total_count"] == 3
        assert data["limit"] == 50  # Default limit
        assert data["offset"] == 0  # Default offset
        assert data["has_more"] is False

    @pytest.mark.asyncio
    async def test_get_event_attendees_with_pagination(self, async_client: AsyncClient):
        """Test getting event attendees with pagination"""
        # Arrange - Create an event and register attendees
        event_data = {
            "name": "Tech Conference 2024",
            "location": "Convention Center, Mumbai",
            "start_time": (datetime.now() + timedelta(days=30)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=30, hours=8)).isoformat(),
            "max_capacity": 100,
        }

        event_response = await async_client.post("/events/", json=event_data)
        event_id = event_response.json()["id"]

        # Register multiple attendees
        attendees_data = [
            {"name": f"Attendee {i}", "email": f"attendee{i}@example.com"}
            for i in range(1, 6)  # 5 attendees
        ]

        for attendee_data in attendees_data:
            await async_client.post(f"/events/{event_id}/register", json=attendee_data)

        # Act - Test pagination
        response = await async_client.get(
            f"/events/{event_id}/attendees?limit=3&offset=0"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["attendees"]) == 3
        assert data["total_count"] == 5
        assert data["limit"] == 3
        assert data["offset"] == 0
        assert data["has_more"] is True

    @pytest.mark.asyncio
    async def test_get_event_attendees_event_not_found(self, async_client: AsyncClient):
        """Test getting attendees for non-existent event"""
        # Act
        response = await async_client.get("/events/999/attendees")

        # Assert
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_full_event_workflow(self, async_client: AsyncClient):
        """Test complete workflow: create event, register attendees, get attendees"""
        # Step 1: Create event
        event_data = {
            "name": "Full Workflow Test Event",
            "location": "Test Location",
            "start_time": (datetime.now() + timedelta(days=30)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=30, hours=4)).isoformat(),
            "max_capacity": 3,
        }

        event_response = await async_client.post("/events/", json=event_data)
        assert event_response.status_code == 201
        event_id = event_response.json()["id"]

        # Step 2: Register attendees
        attendees_data = [
            {"name": "Alice Johnson", "email": "alice@example.com"},
            {"name": "Bob Smith", "email": "bob@example.com"},
            {"name": "Charlie Brown", "email": "charlie@example.com"},
        ]

        for attendee_data in attendees_data:
            registration_response = await async_client.post(
                f"/events/{event_id}/register", json=attendee_data
            )
            assert registration_response.status_code == 201

        # Step 3: Verify event is now full
        fourth_attendee = {"name": "David Wilson", "email": "david@example.com"}
        full_response = await async_client.post(
            f"/events/{event_id}/register", json=fourth_attendee
        )
        assert full_response.status_code == 409  # Capacity exceeded

        # Step 4: Get all attendees
        attendees_response = await async_client.get(f"/events/{event_id}/attendees")
        assert attendees_response.status_code == 200
        attendees_data = attendees_response.json()
        assert len(attendees_data["attendees"]) == 3
        assert attendees_data["total_count"] == 3

        # Step 5: Get all events and verify our event is there
        events_response = await async_client.get("/events/")
        assert events_response.status_code == 200
        events_list = events_response.json()
        assert len(events_list) >= 1

        # Find our event in the list
        our_event = next((e for e in events_list if e["id"] == event_id), None)
        assert our_event is not None
        assert our_event["current_attendee_count"] == 3
        assert our_event["available_spots"] == 0
        assert our_event["is_full"] is True

    @pytest.mark.asyncio
    async def test_get_events_with_timezone_default(self, async_client: AsyncClient):
        """Test getting events with default timezone (Asia/Kolkata)"""
        # Arrange - Create an event with known UTC times
        utc_now = datetime.now(pytz.UTC)
        event_data = {
            "name": "Timezone Test Event",
            "location": "Mumbai",
            "start_time": (utc_now + timedelta(days=1)).isoformat(),
            "end_time": (utc_now + timedelta(days=1, hours=2)).isoformat(),
            "max_capacity": 50,
        }

        await async_client.post("/events/", json=event_data)

        # Act - Get events without timezone parameter (should default to Asia/Kolkata)
        response = await async_client.get("/events/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

        event = data[0]
        # Parse the returned timestamp
        start_time_str = event["start_time"]
        end_time_str = event["end_time"]

        # The times should be in IST (UTC+5:30)
        assert "+05:30" in start_time_str
        assert "+05:30" in end_time_str

    @pytest.mark.asyncio
    async def test_get_events_with_timezone_ist(self, async_client: AsyncClient):
        """Test getting events with explicit IST timezone"""
        # Arrange - Create an event
        utc_now = datetime.now(pytz.UTC)
        event_data = {
            "name": "IST Timezone Test Event",
            "location": "Delhi",
            "start_time": (utc_now + timedelta(days=2)).isoformat(),
            "end_time": (utc_now + timedelta(days=2, hours=3)).isoformat(),
            "max_capacity": 100,
        }

        await async_client.post("/events/", json=event_data)

        # Act - Get events with IST timezone
        response = await async_client.get("/events/?timezone=Asia/Kolkata")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

        event = data[0]
        start_time_str = event["start_time"]
        end_time_str = event["end_time"]

        # The times should be in IST (UTC+5:30)
        assert "+05:30" in start_time_str
        assert "+05:30" in end_time_str

    @pytest.mark.asyncio
    async def test_get_events_with_timezone_us_eastern(self, async_client: AsyncClient):
        """Test getting events with US Eastern timezone"""
        # Arrange - Create an event
        utc_now = datetime.now(pytz.UTC)
        event_data = {
            "name": "US Eastern Timezone Test Event",
            "location": "New York",
            "start_time": (utc_now + timedelta(days=3)).isoformat(),
            "end_time": (utc_now + timedelta(days=3, hours=4)).isoformat(),
            "max_capacity": 200,
        }

        await async_client.post("/events/", json=event_data)

        # Act - Get events with US Eastern timezone
        response = await async_client.get("/events/?timezone=US/Eastern")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

        event = data[0]
        start_time_str = event["start_time"]
        end_time_str = event["end_time"]

        # The times should be in US Eastern (UTC-5:00 or UTC-4:00 depending on DST)
        assert "-05:00" in start_time_str or "-04:00" in start_time_str
        assert "-05:00" in end_time_str or "-04:00" in end_time_str

    @pytest.mark.asyncio
    async def test_get_events_with_timezone_utc(self, async_client: AsyncClient):
        """Test getting events with UTC timezone"""
        # Arrange - Create an event
        utc_now = datetime.now(pytz.UTC)
        event_data = {
            "name": "UTC Timezone Test Event",
            "location": "London",
            "start_time": (utc_now + timedelta(days=4)).isoformat(),
            "end_time": (utc_now + timedelta(days=4, hours=5)).isoformat(),
            "max_capacity": 150,
        }

        await async_client.post("/events/", json=event_data)

        # Act - Get events with UTC timezone
        response = await async_client.get("/events/?timezone=UTC")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

        event = data[0]
        start_time_str = event["start_time"]
        end_time_str = event["end_time"]

        # The times should be in UTC (+00:00)
        assert "+00:00" in start_time_str
        assert "+00:00" in end_time_str

    @pytest.mark.asyncio
    async def test_get_events_with_invalid_timezone(self, async_client: AsyncClient):
        """Test getting events with invalid timezone parameter"""
        # Act - Get events with invalid timezone
        response = await async_client.get("/events/?timezone=Invalid/Timezone")

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "Invalid timezone" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_events_timezone_conversion_accuracy(
        self, async_client: AsyncClient
    ):
        """Test that timezone conversion is mathematically accurate"""
        # Arrange - Create event with specific UTC time
        # Using a specific time to ensure predictable conversion
        utc_time = datetime(2024, 12, 1, 10, 0, 0, tzinfo=pytz.UTC)  # 10:00 AM UTC

        event_data = {
            "name": "Timezone Accuracy Test Event",
            "location": "Global",
            "start_time": utc_time.isoformat(),
            "end_time": (utc_time + timedelta(hours=2)).isoformat(),
            "max_capacity": 100,
        }

        await async_client.post("/events/", json=event_data)

        # Act - Get events with different timezones
        ist_response = await async_client.get("/events/?timezone=Asia/Kolkata")
        utc_response = await async_client.get("/events/?timezone=UTC")

        # Assert
        assert ist_response.status_code == 200
        assert utc_response.status_code == 200

        ist_data = ist_response.json()
        utc_data = utc_response.json()

        assert len(ist_data) >= 1
        assert len(utc_data) >= 1

        # Parse times
        ist_start = ist_data[0]["start_time"]
        utc_start = utc_data[0]["start_time"]

        # IST should be UTC+5:30, so 10:00 UTC = 15:30 IST
        assert "15:30:00+05:30" in ist_start
        assert "10:00:00+00:00" in utc_start

    @pytest.mark.asyncio
    async def test_get_events_with_pagination_and_timezone(
        self, async_client: AsyncClient
    ):
        """Test getting events with both pagination and timezone parameters"""
        # Arrange - Create multiple events
        utc_now = datetime.now(pytz.UTC)
        events_data = [
            {
                "name": f"Pagination Timezone Test Event {i}",
                "location": f"Location {i}",
                "start_time": (utc_now + timedelta(days=i + 5)).isoformat(),
                "end_time": (utc_now + timedelta(days=i + 5, hours=2)).isoformat(),
                "max_capacity": 50,
            }
            for i in range(1, 4)
        ]

        # Create events
        for event_data in events_data:
            await async_client.post("/events/", json=event_data)

        # Act - Test pagination with timezone
        response = await async_client.get(
            "/events/?limit=2&offset=0&timezone=US/Eastern"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 2

        # Check that timezone conversion is applied
        for event in data:
            start_time_str = event["start_time"]
            end_time_str = event["end_time"]
            # Should be in US Eastern time
            assert "-05:00" in start_time_str or "-04:00" in start_time_str
            assert "-05:00" in end_time_str or "-04:00" in end_time_str
