from __future__ import unicode_literals

from django.db import models


class ActsUsers(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    person_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    pass_field = models.CharField(db_column='pass', max_length=32, blank=True)  # Field renamed because it was a Python reserved word.
    registered = models.DateField()
    login = models.DateField()
    contact = models.BooleanField()
    alumni = models.BooleanField()
    publishemail = models.BooleanField()
    hearabout = models.TextField()  # This field type is a guess.
    occupation = models.CharField(max_length=255, blank=True)
    graduation = models.CharField(max_length=255, blank=True)
    tel = models.CharField(max_length=50, blank=True)
    dbemail = models.NullBooleanField()
    dbphone = models.NullBooleanField()
    forumnotify = models.NullBooleanField()
    threadmessages = models.NullBooleanField()
    reversetime = models.BooleanField()
    resetcode = models.CharField(max_length=32, blank=True)
    upgraded_at = models.DateTimeField(blank=True, null=True)
    is_email_verified = models.BooleanField()
    profile_picture_url = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'acts_users'


#Perplexing
class ActsEvents(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    socid = models.IntegerField(blank=True, null=True)
    text = models.CharField(max_length=255)
    endtime = models.TimeField()
    starttime = models.TimeField()
    date = models.DateField()
    description = models.TextField()  # This field type is a guess.
    linkid = models.IntegerField()

    class Meta:
        db_table = 'acts_events'


class ActsExternalUsers(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user_id = models.IntegerField(blank=True, null=True)
    person_id = models.IntegerField(blank=True, null=True)
    service = models.CharField(max_length=50)
    remote_id = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, blank=True)
    token = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    profile_picture_url = models.CharField(max_length=255, blank=True)
    last_login_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acts_external_users'


class ActsKnowledgebase(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    pageid = models.IntegerField(blank=True, null=True)
    userid = models.IntegerField(blank=True, null=True)
    text = models.TextField()  # This field type is a guess.
    date = models.DateTimeField()

    class Meta:
        db_table = 'acts_knowledgebase'


class ActsNameAliases(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    person_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'acts_name_aliases'


class ActsSimilarNames(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name1 = models.CharField(max_length=255)
    name2 = models.CharField(max_length=255)
    equivalence = models.BooleanField()

    class Meta:
        db_table = 'acts_similar_names'




#API Stuff
class ActsApiAccessTokens(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    client_id = models.IntegerField()
    user_id = models.IntegerField(blank=True, null=True)
    token = models.CharField(unique=True, max_length=255)
    expires_at = models.IntegerField(blank=True, null=True)
    scope = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'acts_api_access_tokens'


class ActsApiApps(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user_id = models.IntegerField(blank=True, null=True)
    organisation_id = models.IntegerField(blank=True, null=True)
    random_id = models.CharField(max_length=255)
    redirect_uris = models.TextField()  # This field type is a guess.
    secret = models.CharField(max_length=255)
    allowed_grant_types = models.TextField()  # This field type is a guess.
    name = models.CharField(max_length=255)
    description = models.TextField()  # This field type is a guess.
    app_type = models.CharField(max_length=20)
    is_admin = models.BooleanField()
    website = models.CharField(max_length=1024)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'acts_api_apps'


class ActsApiAuthCodes(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    client_id = models.IntegerField()
    user_id = models.IntegerField(blank=True, null=True)
    token = models.CharField(unique=True, max_length=255)
    redirect_uri = models.TextField()  # This field type is a guess.
    expires_at = models.IntegerField(blank=True, null=True)
    scope = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'acts_api_auth_codes'


class ActsApiAuthorisations(models.Model):
    externalapp_id = models.IntegerField()
    user_id = models.IntegerField()

    class Meta:
        db_table = 'acts_api_authorisations'


class ActsApiRefreshTokens(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    client_id = models.IntegerField()
    user_id = models.IntegerField(blank=True, null=True)
    token = models.CharField(unique=True, max_length=255)
    expires_at = models.IntegerField(blank=True, null=True)
    scope = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'acts_api_refresh_tokens'

#Done (i think)
class ActsShows(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    image_id = models.IntegerField(blank=True, null=True)
    socid = models.IntegerField(blank=True, null=True)
    venid = models.IntegerField(blank=True, null=True)
    authorizeid = models.IntegerField(blank=True, null=True)
    primaryref = models.IntegerField(unique=True, blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)  # This field type is a guess.
    facebook_id = models.CharField(max_length=50, blank=True)
    twitter_id = models.CharField(max_length=50, blank=True)
    slug = models.CharField(unique=True, max_length=128, blank=True)
    dates = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    prices = models.CharField(max_length=255, blank=True)
    photourl = models.TextField(blank=True)  # This field type is a guess.
    venue = models.CharField(max_length=255, blank=True)
    excludedate = models.DateField(blank=True, null=True)
    society = models.CharField(max_length=255, blank=True)
    techsend = models.BooleanField()
    actorsend = models.BooleanField()
    audextra = models.TextField(blank=True)  # This field type is a guess.
    entered = models.BooleanField()
    entryexpiry = models.DateField()
    category = models.CharField(max_length=255)
    bookingcode = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField()
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)
    freebase_id = models.CharField(max_length=255, blank=True)
    facebookurl = models.CharField(max_length=2083, blank=True)
    otherurl = models.CharField(max_length=2083, blank=True)
    onlinebookingurl = models.CharField(max_length=2083, blank=True)

    class Meta:
        db_table = 'acts_shows'


#Done
class ActsAuditions(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    showid = models.IntegerField(blank=True, null=True)
    date = models.DateField()
    starttime = models.TimeField()
    endtime = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=255)
    display = models.BooleanField()
    nonscheduled = models.BooleanField()

    class Meta:
        db_table = 'acts_auditions'


#Done
class ActsApplications(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    showid = models.IntegerField(blank=True, null=True)
    socid = models.IntegerField(blank=True, null=True)
    text = models.TextField()  # This field type is a guess.
    deadlinedate = models.DateField()
    furtherinfo = models.TextField()  # This field type is a guess.
    deadlinetime = models.TimeField()

    class Meta:
        db_table = 'acts_applications'


#Done
class ActsPendingaccess(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    issuerid = models.IntegerField()
    rid = models.IntegerField()
    email = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    creationdate = models.DateField()

    class Meta:
        db_table = 'acts_pendingaccess'


#Done
class ActsAccess(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    uid = models.IntegerField(blank=True, null=True)
    issuerid = models.IntegerField(blank=True, null=True)
    revokeid = models.IntegerField(blank=True, null=True)
    rid = models.IntegerField()
    type = models.CharField(max_length=20)
    creationdate = models.DateField()
    revokedate = models.DateField(blank=True, null=True)
    contact = models.BooleanField()

    class Meta:
        db_table = 'acts_access'


#Done
class ActsTechies(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    showid = models.IntegerField(blank=True, null=True)
    positions = models.TextField()  # This field type is a guess.
    contact = models.TextField()  # This field type is a guess.
    deadline = models.BooleanField()
    deadlinetime = models.TimeField()
    expiry = models.DateField()
    display = models.BooleanField()
    remindersent = models.BooleanField()
    techextra = models.TextField()  # This field type is a guess.
    lastupdated = models.DateTimeField()

    class Meta:
        db_table = 'acts_techies'


#Done
class ActsPeopleData(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    image_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)  # This field type is a guess.
    slug = models.CharField(unique=True, max_length=128, blank=True)
    mapto = models.IntegerField()
    norobots = models.BooleanField()

    class Meta:
        db_table = 'acts_people_data'


#Done
class ActsPerformances(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    sid = models.IntegerField(blank=True, null=True)
    venid = models.IntegerField(blank=True, null=True)
    startdate = models.DateField()
    enddate = models.DateField()
    excludedate = models.DateField(blank=True, null=True)
    time = models.TimeField()
    venue = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'acts_performances'


#Done
class ActsShowsPeopleLink(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    sid = models.IntegerField(blank=True, null=True)
    pid = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=20)
    role = models.CharField(max_length=255)
    order = models.IntegerField()

    class Meta:
        db_table = 'acts_shows_people_link'


#Done
class ActsSocieties(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    image_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)  # This field type is a guess.
    facebook_id = models.CharField(max_length=50, blank=True)
    twitter_id = models.CharField(max_length=50, blank=True)
    shortname = models.CharField(max_length=100)
    college = models.CharField(max_length=100, blank=True)
    affiliate = models.BooleanField()
    logourl = models.CharField(max_length=255, blank=True)
    slug = models.CharField(unique=True, max_length=128, blank=True)
    expires = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=255)
    address = models.TextField(blank=True)  # This field type is a guess.
    latitude = models.TextField(blank=True)  # This field type is a guess.
    longitude = models.TextField(blank=True)  # This field type is a guess.

    class Meta:
        db_table = 'acts_societies'

        
