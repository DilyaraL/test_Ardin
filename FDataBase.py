import json
from flask import Flask, jsonify, request, render_template, Response, abort
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, DefaultClause, \
    PrimaryKeyConstraint, Index, Enum, text, select, join, exists
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, scoped_session, session
import psycopg2
metadata = MetaData()

user = Table(
    'user', metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")),
    Column('email', String, unique=True, nullable=False),
    Column('password', String),
    Column('position_id', UUID(as_uuid=True), ForeignKey('position.id', ondelete='SET NULL')),
)

role_permission = Table(
    'role_permission', metadata,
    Column('user_id', UUID(as_uuid=True),ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
    Column('permission', Enum('USER_CREATE', 'USER_READ', 'USER_UPDATE', 'USER_DELETE', name='permission_enum'),
            nullable=False),
    PrimaryKeyConstraint('user_id', 'permission'),
    Index('idx_role_permission', 'user_id', 'permission'),

)

position = Table(
    'position', metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")),
    Column('title', String, nullable=False),
)
