from tortoise import fields, models

class Users(models.Model):
    android_id = fields.CharField(max_length=128, pk=True)
    name = fields.CharField(max_length=10, null=True)
    age = fields.IntField(null=True)
    disease = fields.CharField(max_length=225, null=True)
    gender = fields.CharField(max_length=1, null=True)

    class Meta:
        table = "Users"

class EmergencyInfo(models.Model):
    user = fields.OneToOneField('models.Users', related_name="emergencyinfo")
    emergency_name = fields.CharField(max_length=10, null=True)
    emergency_phone = fields.CharField(max_length=11, null=True)
    relation = fields.CharField(max_length=10, null=True)

    class Meta:
        table = "EmergencyInfo"


class Objects(models.Model):
    user = fields.ForeignKeyField('models.Users', related_name="objects")
    name = fields.CharField(max_length=32)
    scene = fields.CharField(max_length=32)
    x0 = fields.IntField()
    y0 = fields.IntField()
    objects = fields.CharField(max_length=5000)

    class Meta:
        table = "Objects"


class Emergencys(models.Model):
    user = fields.ForeignKeyField('models.Users', related_name="emergencys")
    type = fields.CharField(max_length=32)
    context = fields.CharField(max_length=500)
    create_time = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "Emergencys"

class History(models.Model):
    user = fields.ForeignKeyField('models.Users', related_name="history")
    history = fields.CharField(max_length=5000)
    create_time = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "History"
