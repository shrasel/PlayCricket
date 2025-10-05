"""Tests for Venue model."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


@pytest.mark.asyncio
@pytest.mark.unit
class TestVenueModel:
    """Test Venue model basic functionality"""
    
    async def test_create_venue_with_required_fields(self, test_db: AsyncSession):
        """Test creating a venue with only required fields"""
        from app.models.venue import Venue
        
        venue = Venue(
            name="Wankhede Stadium",
        )
        
        test_db.add(venue)
        await test_db.commit()
        await test_db.refresh(venue)
        
        assert venue.id is not None
        assert venue.public_id is not None  # Should auto-generate ULID
        assert venue.name == "Wankhede Stadium"
        assert venue.created_at is not None
        
    async def test_create_venue_with_all_fields(self, test_db: AsyncSession):
        """Test creating a venue with all optional fields"""
        from app.models.venue import Venue
        
        venue = Venue(
            name="Eden Gardens",
            city="Kolkata",
            country_code="IND",
            timezone_name="Asia/Kolkata",
            ends_names="High Court End, Pavilion End",
        )
        
        test_db.add(venue)
        await test_db.commit()
        await test_db.refresh(venue)
        
        assert venue.name == "Eden Gardens"
        assert venue.city == "Kolkata"
        assert venue.country_code == "IND"
        assert venue.timezone_name == "Asia/Kolkata"
        assert venue.ends_names == "High Court End, Pavilion End"
        
    async def test_venue_public_id_is_unique(self, test_db: AsyncSession):
        """Test that public_id is unique across venues"""
        from app.models.venue import Venue
        
        venue1 = Venue(name="Venue One")
        venue2 = Venue(name="Venue Two")
        
        test_db.add_all([venue1, venue2])
        await test_db.commit()
        
        assert venue1.public_id != venue2.public_id
        
    async def test_venue_name_must_be_unique(self, test_db: AsyncSession):
        """Test that venue name must be unique"""
        from app.models.venue import Venue
        
        venue1 = Venue(name="M. Chinnaswamy Stadium")
        test_db.add(venue1)
        await test_db.commit()
        
        # Try to create another venue with same name
        venue2 = Venue(name="M. Chinnaswamy Stadium")
        test_db.add(venue2)
        
        with pytest.raises(IntegrityError):
            await test_db.commit()
            
    async def test_venue_name_is_required(self, test_db: AsyncSession):
        """Test that name is required"""
        from app.models.venue import Venue
        
        with pytest.raises((IntegrityError, ValueError)):
            venue = Venue()
            test_db.add(venue)
            await test_db.commit()
            
    async def test_get_venue_by_public_id(self, test_db: AsyncSession):
        """Test retrieving venue by public_id"""
        from app.models.venue import Venue
        
        venue = Venue(
            name="Lord's Cricket Ground",
            city="London",
            country_code="ENG",
        )
        test_db.add(venue)
        await test_db.commit()
        await test_db.refresh(venue)
        
        # Query by public_id
        result = await test_db.execute(
            select(Venue).where(Venue.public_id == venue.public_id)
        )
        found_venue = result.scalar_one()
        
        assert found_venue.id == venue.id
        assert found_venue.name == "Lord's Cricket Ground"
        assert found_venue.city == "London"
        
    async def test_venue_str_representation(self, test_db: AsyncSession):
        """Test venue string representation"""
        from app.models.venue import Venue
        
        # Test with city
        venue1 = Venue(name="MCG", city="Melbourne")
        assert str(venue1) == "MCG, Melbourne"
        
        # Test without city
        venue2 = Venue(name="The Oval")
        assert str(venue2) == "The Oval"
        
    async def test_venue_dict_representation(self, test_db: AsyncSession):
        """Test venue to_dict method"""
        from app.models.venue import Venue
        
        venue = Venue(
            name="Dubai International Cricket Stadium",
            city="Dubai",
            country_code="UAE",
            timezone_name="Asia/Dubai",
            ends_names="North End, South End",
        )
        test_db.add(venue)
        await test_db.commit()
        await test_db.refresh(venue)
        
        venue_dict = venue.to_dict()
        
        assert venue_dict["public_id"] == venue.public_id
        assert venue_dict["name"] == "Dubai International Cricket Stadium"
        assert venue_dict["city"] == "Dubai"
        assert venue_dict["country_code"] == "UAE"
        assert venue_dict["timezone_name"] == "Asia/Dubai"
        assert venue_dict["ends_names"] == "North End, South End"
        assert "created_at" in venue_dict


@pytest.mark.asyncio
@pytest.mark.unit
class TestVenueTimezones:
    """Test Venue timezone handling"""
    
    async def test_venue_with_valid_timezone(self, test_db: AsyncSession):
        """Test creating venue with valid timezone"""
        from app.models.venue import Venue
        
        valid_timezones = [
            "Asia/Kolkata",
            "Australia/Sydney",
            "Europe/London",
            "America/New_York",
            "Pacific/Auckland",
        ]
        
        for tz in valid_timezones:
            venue = Venue(
                name=f"Stadium {tz}",
                timezone_name=tz,
            )
            test_db.add(venue)
            await test_db.commit()
            await test_db.refresh(venue)
            
            assert venue.timezone_name == tz
            await test_db.delete(venue)
            await test_db.commit()
            
    async def test_venue_without_timezone(self, test_db: AsyncSession):
        """Test that timezone is optional"""
        from app.models.venue import Venue
        
        venue = Venue(name="Test Stadium")
        test_db.add(venue)
        await test_db.commit()
        await test_db.refresh(venue)
        
        assert venue.timezone_name is None


@pytest.mark.asyncio
@pytest.mark.unit
class TestVenueEnds:
    """Test Venue ends/boundaries naming"""
    
    async def test_venue_with_ends_names(self, test_db: AsyncSession):
        """Test storing cricket ground end names"""
        from app.models.venue import Venue
        
        venue = Venue(
            name="Adelaide Oval",
            ends_names="Cathedral End, River Torrens End",
        )
        test_db.add(venue)
        await test_db.commit()
        await test_db.refresh(venue)
        
        assert venue.ends_names == "Cathedral End, River Torrens End"
        assert "Cathedral End" in venue.ends_names
        assert "River Torrens End" in venue.ends_names
        
    async def test_venue_without_ends_names(self, test_db: AsyncSession):
        """Test that ends_names is optional"""
        from app.models.venue import Venue
        
        venue = Venue(name="New Stadium")
        test_db.add(venue)
        await test_db.commit()
        await test_db.refresh(venue)
        
        assert venue.ends_names is None


@pytest.mark.asyncio
@pytest.mark.unit
class TestVenueCountries:
    """Test Venue country codes"""
    
    async def test_venue_with_country_codes(self, test_db: AsyncSession):
        """Test various country codes"""
        from app.models.venue import Venue
        
        test_cases = [
            ("Wankhede Stadium", "IND"),
            ("Lord's", "ENG"),
            ("MCG", "AUS"),
            ("Eden Park", "NZL"),
            ("Gaddafi Stadium", "PAK"),
        ]
        
        for name, code in test_cases:
            venue = Venue(name=name, country_code=code)
            test_db.add(venue)
            await test_db.commit()
            await test_db.refresh(venue)
            
            assert venue.country_code == code
            await test_db.delete(venue)
            await test_db.commit()


@pytest.mark.asyncio
@pytest.mark.unit
class TestVenueTimestamps:
    """Test Venue timestamp behavior"""
    
    async def test_created_at_auto_set(self, test_db: AsyncSession):
        """Test that created_at is automatically set"""
        from app.models.venue import Venue
        from datetime import datetime, timezone
        
        before = datetime.now(timezone.utc)
        venue = Venue(name="Test Venue")
        
        test_db.add(venue)
        await test_db.commit()
        await test_db.refresh(venue)
        after = datetime.now(timezone.utc)
        
        assert venue.created_at is not None
        assert before <= venue.created_at <= after
        
    async def test_updated_at_auto_updates(self, test_db: AsyncSession):
        """Test that updated_at is automatically updated on changes"""
        from app.models.venue import Venue
        import asyncio
        
        venue = Venue(name="Original Name")
        test_db.add(venue)
        await test_db.commit()
        await test_db.refresh(venue)
        
        original_updated_at = venue.updated_at
        
        # Wait a bit and update
        await asyncio.sleep(0.1)
        venue.name = "Updated Name"
        await test_db.commit()
        await test_db.refresh(venue)
        
        assert venue.updated_at > original_updated_at
