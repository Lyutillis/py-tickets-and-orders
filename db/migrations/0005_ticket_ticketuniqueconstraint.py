# Generated by Django 4.0.2 on 2023-11-07 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0004_remove_ticket_ticketuniqueconstraint'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='ticket',
            constraint=models.UniqueConstraint(fields=('movie_session', 'row', 'seat'), name='TicketUniqueConstraint'),
        ),
    ]