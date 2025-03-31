from django.db import migrations, models

def calculate_pax_per_room(apps, schema_editor):
    Room = apps.get_model('rooms', 'Room')
    for room in Room.objects.all():
        # Calculate pax_per_room from capacity and rooms_count
        if room.rooms_count > 0:
            room.pax_per_room = room.capacity // room.rooms_count
        else:
            room.pax_per_room = 2  # Default value
        room.save()

class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='rooms_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='room',
            name='pax_per_room',
            field=models.IntegerField(default=2),
        ),
        migrations.RunPython(calculate_pax_per_room),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together={('category', 'location')},
        ),
    ] 