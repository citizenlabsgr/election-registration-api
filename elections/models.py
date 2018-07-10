from typing import List

from django.db import models

import log
import pendulum
import requests
from model_utils.models import TimeStampedModel

from . import helpers


class DistrictCategory(TimeStampedModel):
    """Types of regions bound to ballot items."""

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "District Categories"

    def __str__(self) -> str:
        return self.name


class District(TimeStampedModel):
    """Districts bound to ballot items."""

    category = models.ForeignKey(DistrictCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    population = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        unique_together = ['category', 'name']
        ordering = ['-population']

    def __str__(self) -> str:
        return self.name


class Election(TimeStampedModel):
    """Point in time where voters can cast opinions on ballot items."""

    name = models.CharField(max_length=100)
    date = models.DateField()

    active = models.BooleanField(default=False)
    reference_url = models.URLField(blank=True, null=True)

    mi_sos_id = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        unique_together = ['date', 'name']
        ordering = ['-date']

    def __str__(self) -> str:
        return ' | '.join(self.mi_sos_name)

    @property
    def mi_sos_name(self) -> List[str]:
        return [
            self.name,
            pendulum.parse(self.date.isoformat()).format("dddd, MMMM D, YYYY"),
        ]


class Poll(TimeStampedModel):
    """Specific region where all voters share a ballot."""

    county = models.ForeignKey(
        District, related_name='counties', on_delete=models.CASCADE
    )
    jurisdiction = models.ForeignKey(
        District, related_name='jurisdictions', on_delete=models.CASCADE
    )
    ward = models.CharField(max_length=2, blank=True)
    precinct = models.CharField(max_length=3, blank=True)

    mi_sos_id = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        unique_together = ['county', 'jurisdiction', 'ward', 'precinct']

    def __str__(self) -> str:
        return ' | '.join(self.mi_sos_name)

    @property
    def mi_sos_name(self) -> List[str]:
        if self.ward and self.precinct:
            ward_precinct = f"Ward {self.ward} Precinct {self.precinct}"
        elif self.ward:
            # Extra space is intentional to match the MI SOS website format
            ward_precinct = f"Ward {self.ward} "
        else:
            assert (
                self.precinct
            ), f"Ward and precinct are missing: id={self.id} mi_sos_id={self.mi_sos_id}"
            # Extra space is intentional to match the MI SOS website format
            ward_precinct = f" Precinct {self.precinct}"
        return [
            f"{self.county} County, Michigan",
            f"{self.jurisdiction}, {ward_precinct}",
        ]


class RegistrationStatus(models.Model):
    """Status of a particular voter's registration."""

    registered = models.BooleanField()
    poll = models.ForeignKey(Poll, null=True, on_delete=models.SET_NULL)
    districts: List[
        District
    ]  # Act like 'ManytoManyField', but this model is never saved

    def save(self, *args, **kwargs):
        raise NotImplementedError


class Voter(models.Model):
    """Data needed to look up Michigan voter registration status."""

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField()
    zip_code = models.CharField(max_length=10)

    def __repr__(self) -> str:
        birth = pendulum.parse(str(self.birth_date)).format("YYYY-MM-DD")
        return f"<voter: {self}, birth={birth}, zip={self.zip_code}>"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def birth_month(self) -> str:
        return pendulum.parse(str(self.birth_date)).format("MMMM")

    @property
    def birth_year(self) -> int:
        return self.birth_date.year

    def fetch_registration_status(self) -> RegistrationStatus:
        data = helpers.fetch_registration_status_data(self)

        districts: List[District] = []
        county = jurisdiction = None

        for category_name, district_name in sorted(data['districts'].items()):
            if not (category_name and district_name):
                log.warn("Skipped blank MI SOS district")
                continue

            if category_name in ["Ward", "Precinct"]:
                log.debug(f"Skipped category: {category_name}")
                continue

            category, created = DistrictCategory.objects.get_or_create(
                name=category_name
            )
            if created:
                log.info(f"New category: {category}")

            if category.name == "County":
                district_name = district_name.replace(" County", "")
            district, created = District.objects.get_or_create(
                category=category, name=district_name
            )
            if created:
                log.info(f"New district: {district}")

            districts.append(district)

            if district.category.name == "County":
                county = district
            if district.category.name == "Jurisdiction":
                jurisdiction = district

        assert all(
            [
                county,
                jurisdiction,
                data['districts']['Ward'],
                data['districts']['Precinct'],
            ]
        ), f"Missing poll information: {data}"
        poll, created = Poll.objects.get_or_create(
            county=county,
            jurisdiction=jurisdiction,
            ward=int(data['districts']['Ward']),
            precinct=data['districts']['Precinct'],
        )
        if created:
            log.info(f"New poll: {poll}")

        status = RegistrationStatus(registered=data['registered'], poll=poll)
        status.districts = districts

        return status

    def save(self, *args, **kwargs):
        raise NotImplementedError


class Ballot(TimeStampedModel):
    """Full ballot bound to a particular polling location."""

    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

    mi_sos_html = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return ' | '.join(self.mi_sos_name)

    @property
    def mi_sos_url(self) -> str:
        return self.build_mi_sos_url(
            election_id=self.election.mi_sos_id, poll_id=self.poll.mi_sos_id
        )

    @property
    def mi_sos_name(self) -> List[str]:
        return self.election.mi_sos_name + self.poll.mi_sos_name

    @staticmethod
    def build_mi_sos_url(election_id: int, poll_id: int) -> str:
        assert election_id, "MI SOS election ID is missing"
        assert poll_id, "MI SOS poll ID is missing"
        base = "https://webapps.sos.state.mi.us/MVIC/SampleBallot.aspx"
        params = f"d={poll_id}&ed={election_id}"
        return f"{base}?{params}"

    def update_mi_sos_html(self) -> bool:
        url = self.mi_sos_url

        log.info(f"Fetching {url}")
        response = requests.get(url)

        html = response.text
        for text in self.mi_sos_name:
            assert text in html, f"Expected {text!r}: {url}"

        updated = self.mi_sos_html != html
        self.mi_sos_html = html

        return updated


class BallotItem(TimeStampedModel):

    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    poll = models.ForeignKey(
        Poll, on_delete=models.CASCADE, null=True
    )  # TODO: remove null
    district = models.ForeignKey(
        District, on_delete=models.CASCADE
    )  # TODO: Delete this

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    reference_url = models.URLField(blank=True, null=True)

    class Meta:
        abstract = True
        unique_together = ['election', 'district', 'name']


class Proposal(BallotItem):
    """Ballot item with a boolean outcome."""


class Party(TimeStampedModel):
    """Affiliation for a particular candidate."""

    name = models.CharField(max_length=50)


class Candidate(TimeStampedModel):
    """Individual running for a particular position."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    reference_url = models.URLField(blank=True, null=True)
    party = models.ForeignKey(
        Party, blank=True, null=True, on_delete=models.SET_NULL
    )


class Position(BallotItem):
    """Ballot item selecting one ore more candidates."""

    candidates = models.ManyToManyField(Candidate)
    seats = models.PositiveIntegerField(default=1)
