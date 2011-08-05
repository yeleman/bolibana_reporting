# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Period'
        db.create_table('bolibana_reporting_period', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_on', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_on', self.gf('django.db.models.fields.DateTimeField')()),
            ('period_type', self.gf('django.db.models.fields.CharField')(default='custom', max_length=15)),
        ))
        db.send_create_signal('bolibana_reporting', ['Period'])

        # Adding unique constraint on 'Period', fields ['start_on', 'end_on', 'period_type']
        db.create_unique('bolibana_reporting_period', ['start_on', 'end_on', 'period_type'])

        # Adding model 'Entity'
        db.create_table('bolibana_reporting_entity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=15, db_index=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='entities', to=orm['bolibana_reporting.EntityType'])),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['bolibana_reporting.Entity'])),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('bolibana_reporting', ['Entity'])

        # Adding model 'EntityType'
        db.create_table('bolibana_reporting_entitytype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=15, db_index=True)),
        ))
        db.send_create_signal('bolibana_reporting', ['EntityType'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Period', fields ['start_on', 'end_on', 'period_type']
        db.delete_unique('bolibana_reporting_period', ['start_on', 'end_on', 'period_type'])

        # Deleting model 'Period'
        db.delete_table('bolibana_reporting_period')

        # Deleting model 'Entity'
        db.delete_table('bolibana_reporting_entity')

        # Deleting model 'EntityType'
        db.delete_table('bolibana_reporting_entitytype')


    models = {
        'bolibana_reporting.entity': {
            'Meta': {'object_name': 'Entity'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['bolibana_reporting.Entity']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '15', 'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entities'", 'to': "orm['bolibana_reporting.EntityType']"})
        },
        'bolibana_reporting.entitytype': {
            'Meta': {'object_name': 'EntityType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '15', 'db_index': 'True'})
        },
        'bolibana_reporting.period': {
            'Meta': {'unique_together': "(('start_on', 'end_on', 'period_type'),)", 'object_name': 'Period'},
            'end_on': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period_type': ('django.db.models.fields.CharField', [], {'default': "'custom'", 'max_length': '15'}),
            'start_on': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['bolibana_reporting']
