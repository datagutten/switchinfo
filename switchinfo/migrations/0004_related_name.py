# Generated by Django 3.1.8 on 2022-02-19 08:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('switchinfo', '0003_switchgroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='switch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interfaces', to='switchinfo.switch'),
        ),
        migrations.AlterField(
            model_name='mac',
            name='interface',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='macs', to='switchinfo.interface'),
        ),
        migrations.AlterField(
            model_name='vlan',
            name='on_switch',
            field=models.ManyToManyField(related_name='vlan', to='switchinfo.Switch'),
        ),
    ]