"""seed_test_data

Revision ID: 002_seed_test_data
Revises: 001_initial_schema
Create Date: 2026-02-24 18:10:00

"""

import json

from alembic import op
import sqlalchemy as sa
from passlib.context import CryptContext


# revision identifiers, used by Alembic.
revision = "002_seed_test_data"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_EMAIL = "admin@prisme.com"
DEFAULT_ADMIN_PASSWORD = "admin123"

LAMBIC_CONSULTANT = {
    "first_name": "Lambic",
    "last_name": "Demo",
    "email": "lambic.demo@prisme.com",
    "title": "Senior Cloud and Platform Consultant",
    "summary": "Hands-on consultant profile used to demonstrate how Prism\u00e9 builds rich, modular profiles.",
    "role": "Senior Cloud and Platform Consultant",
    "focus_areas": [
        "Cloud Architecture",
        "Platform Engineering",
        "DevSecOps",
        "Data Platform Delivery",
    ],
    "years_experience": 11,
    "motto": "Ship reliable platforms fast.",
    "profile_name": "LAMBIC Demo - Enterprise Platform Profile",
}

LAMBIC_BLOCKS = [
    {
        "block_type": "project",
        "title": "Global Commerce Platform Modernization",
        "order": 0,
        "client_name": "Northbound Retail Group",
        "project_description": "Modernized a monolithic e-commerce stack into scalable cloud-native services across three regions.",
        "role": "Platform Modernization Lead",
        "technologies": ["AWS", "Kubernetes", "Terraform", "PostgreSQL", "Redis"],
        "start_date": "2023-01-01",
        "end_date": "2024-03-01",
        "is_ongoing": False,
        "duration_months": 15,
    },
    {
        "block_type": "project",
        "title": "Healthcare Data Foundation Rollout",
        "order": 1,
        "client_name": "MediBridge Network",
        "project_description": "Implemented governed ingestion and analytics foundations for clinical and operational reporting.",
        "role": "Cloud Data Platform Architect",
        "technologies": ["Azure", "Databricks", "dbt", "Power BI"],
        "start_date": "2022-02-01",
        "end_date": "2022-12-01",
        "is_ongoing": False,
        "duration_months": 11,
    },
    {
        "block_type": "project",
        "title": "FinOps and Cost Optimization Program",
        "order": 2,
        "client_name": "Lighthouse Financial Services",
        "project_description": "Established cloud cost visibility, budget controls, and rightsizing policies for engineering teams.",
        "role": "FinOps Advisor",
        "technologies": ["AWS", "Cost Explorer", "Grafana", "Python"],
        "start_date": "2024-04-01",
        "end_date": None,
        "is_ongoing": True,
        "duration_months": 10,
    },
    {
        "block_type": "skill",
        "title": "Cloud Architecture",
        "order": 3,
        "proficiency_level": "Expert",
    },
    {
        "block_type": "skill",
        "title": "Kubernetes and Container Platforms",
        "order": 4,
        "proficiency_level": "Expert",
    },
    {
        "block_type": "skill",
        "title": "Infrastructure as Code",
        "order": 5,
        "proficiency_level": "Expert",
    },
    {
        "block_type": "skill",
        "title": "CI and CD Pipeline Design",
        "order": 6,
        "proficiency_level": "Advanced",
    },
    {
        "block_type": "skill",
        "title": "Observability and SRE Practices",
        "order": 7,
        "proficiency_level": "Advanced",
    },
    {
        "block_type": "skill",
        "title": "Data Platform Engineering",
        "order": 8,
        "proficiency_level": "Advanced",
    },
    {
        "block_type": "skill",
        "title": "Security by Design",
        "order": 9,
        "proficiency_level": "Advanced",
    },
    {
        "block_type": "skill",
        "title": "Stakeholder Enablement",
        "order": 10,
        "proficiency_level": "Advanced",
    },
    {
        "block_type": "certification",
        "title": "AWS Certified Solutions Architect - Professional",
        "order": 11,
        "issuing_organization": "Amazon Web Services",
        "issue_date": "2024-01-15",
        "expiry_date": "2027-01-15",
        "credential_id": "AWS-SAP-LAMBIC-001",
        "credential_url": "https://www.credly.com",
    },
    {
        "block_type": "certification",
        "title": "Certified Kubernetes Administrator",
        "order": 12,
        "issuing_organization": "Cloud Native Computing Foundation",
        "issue_date": "2023-06-10",
        "expiry_date": "2026-06-10",
        "credential_id": "CKA-LAMBIC-007",
        "credential_url": "https://www.cncf.io",
    },
    {
        "block_type": "certification",
        "title": "HashiCorp Terraform Associate",
        "order": 13,
        "issuing_organization": "HashiCorp",
        "issue_date": "2022-11-01",
        "expiry_date": None,
        "credential_id": "TFA-LAMBIC-112",
        "credential_url": "https://www.hashicorp.com/certification",
    },
    {
        "block_type": "misc",
        "title": "Delivery Highlights",
        "order": 14,
        "misc_content": "Regularly leads enterprise platform transformations with measurable cost, reliability, and delivery improvements.",
    },
    {
        "block_type": "misc",
        "title": "Leadership and Mentoring",
        "order": 15,
        "misc_content": "Mentors engineering teams on platform ownership, release excellence, and operational readiness.",
    },
]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _insert_block(bind, consultant_id: int, block_data: dict) -> int:
    result = bind.execute(
        sa.text(
            """
            INSERT INTO blocks (
                consultant_id,
                block_type,
                title,
                "order",
                is_active,
                client_name,
                project_description,
                role,
                technologies,
                start_date,
                end_date,
                is_ongoing,
                duration_months,
                proficiency_level,
                misc_content,
                issuing_organization,
                issue_date,
                expiry_date,
                credential_id,
                credential_url,
                created_at,
                updated_at
            )
            VALUES (
                :consultant_id,
                :block_type,
                :title,
                :order,
                1,
                :client_name,
                :project_description,
                :role,
                :technologies,
                :start_date,
                :end_date,
                :is_ongoing,
                :duration_months,
                :proficiency_level,
                :misc_content,
                :issuing_organization,
                :issue_date,
                :expiry_date,
                :credential_id,
                :credential_url,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            """
        ),
        {
            "consultant_id": consultant_id,
            "block_type": block_data["block_type"],
            "title": block_data["title"],
            "order": block_data["order"],
            "client_name": block_data.get("client_name"),
            "project_description": block_data.get("project_description"),
            "role": block_data.get("role"),
            "technologies": json.dumps(block_data.get("technologies", [])) if block_data["block_type"] == "project" else None,
            "start_date": block_data.get("start_date"),
            "end_date": block_data.get("end_date"),
            "is_ongoing": block_data.get("is_ongoing"),
            "duration_months": block_data.get("duration_months"),
            "proficiency_level": block_data.get("proficiency_level"),
            "misc_content": block_data.get("misc_content"),
            "issuing_organization": block_data.get("issuing_organization"),
            "issue_date": block_data.get("issue_date"),
            "expiry_date": block_data.get("expiry_date"),
            "credential_id": block_data.get("credential_id"),
            "credential_url": block_data.get("credential_url"),
        },
    )
    return int(result.lastrowid)


def _snapshot_block(block_id: int, block_data: dict) -> dict:
    base = {
        "id": block_id,
        "title": block_data["title"],
        "block_type": block_data["block_type"],
    }

    if block_data["block_type"] == "project":
        return {
            **base,
            "client_name": block_data.get("client_name"),
            "description": block_data.get("project_description"),
            "role": block_data.get("role"),
            "technologies": block_data.get("technologies", []),
            "duration_months": block_data.get("duration_months"),
            "start_date": block_data.get("start_date"),
            "end_date": block_data.get("end_date"),
            "is_ongoing": block_data.get("is_ongoing"),
        }

    if block_data["block_type"] == "skill":
        return {
            **base,
            "level": block_data.get("proficiency_level"),
        }

    if block_data["block_type"] == "certification":
        return {
            **base,
            "issuing_organization": block_data.get("issuing_organization"),
            "issue_date": block_data.get("issue_date"),
            "expiry_date": block_data.get("expiry_date"),
            "credential_id": block_data.get("credential_id"),
            "credential_url": block_data.get("credential_url"),
        }

    return {
        **base,
        "content": block_data.get("misc_content"),
    }


def upgrade() -> None:
    bind = op.get_bind()

    bind.execute(
        sa.text(
            """
            INSERT INTO admins (username, email, hashed_password, is_active, created_at, updated_at)
            VALUES (:username, :email, :hashed_password, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
        ),
        {
            "username": DEFAULT_ADMIN_USERNAME,
            "email": DEFAULT_ADMIN_EMAIL,
            "hashed_password": pwd_context.hash(DEFAULT_ADMIN_PASSWORD),
        },
    )

    admin_id = int(
        bind.execute(
            sa.text("SELECT id FROM admins WHERE username = :username"),
            {"username": DEFAULT_ADMIN_USERNAME},
        ).scalar_one()
    )

    consultant_insert = bind.execute(
        sa.text(
            """
            INSERT INTO consultants (
                first_name,
                last_name,
                email,
                title,
                summary,
                photo_url,
                role,
                focus_areas,
                years_experience,
                motto,
                created_by_admin_id,
                created_at,
                updated_at
            )
            VALUES (
                :first_name,
                :last_name,
                :email,
                :title,
                :summary,
                NULL,
                :role,
                :focus_areas,
                :years_experience,
                :motto,
                :created_by_admin_id,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            """
        ),
        {
            "first_name": LAMBIC_CONSULTANT["first_name"],
            "last_name": LAMBIC_CONSULTANT["last_name"],
            "email": LAMBIC_CONSULTANT["email"],
            "title": LAMBIC_CONSULTANT["title"],
            "summary": LAMBIC_CONSULTANT["summary"],
            "role": LAMBIC_CONSULTANT["role"],
            "focus_areas": json.dumps(LAMBIC_CONSULTANT["focus_areas"]),
            "years_experience": LAMBIC_CONSULTANT["years_experience"],
            "motto": LAMBIC_CONSULTANT["motto"],
            "created_by_admin_id": admin_id,
        },
    )
    consultant_id = int(consultant_insert.lastrowid)

    selected_block_ids: list[int] = []
    blocks_by_type: dict[str, list[dict]] = {
        "project": [],
        "skill": [],
        "certification": [],
        "misc": [],
    }

    for block in LAMBIC_BLOCKS:
        block_id = _insert_block(bind, consultant_id, block)
        selected_block_ids.append(block_id)
        blocks_by_type[block["block_type"]].append(_snapshot_block(block_id, block))

    profile_snapshot = {
        "consultant": {
            "first_name": LAMBIC_CONSULTANT["first_name"],
            "last_name": LAMBIC_CONSULTANT["last_name"],
            "title": LAMBIC_CONSULTANT["title"],
            "email": LAMBIC_CONSULTANT["email"],
            "photo_url": None,
        },
        "blocks_by_type": blocks_by_type,
        "generated_at": "2026-02-24T18:10:00+00:00",
        "general_customizations": {
            "role": LAMBIC_CONSULTANT["role"],
            "focus_areas": LAMBIC_CONSULTANT["focus_areas"],
            "years_experience": LAMBIC_CONSULTANT["years_experience"],
            "motto": LAMBIC_CONSULTANT["motto"],
        },
    }

    bind.execute(
        sa.text(
            """
            INSERT INTO profiles (
                consultant_id,
                profile_name,
                selected_block_ids,
                profile_data,
                created_by_admin_id,
                created_at,
                updated_at
            )
            VALUES (
                :consultant_id,
                :profile_name,
                :selected_block_ids,
                :profile_data,
                :created_by_admin_id,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            """
        ),
        {
            "consultant_id": consultant_id,
            "profile_name": LAMBIC_CONSULTANT["profile_name"],
            "selected_block_ids": json.dumps(selected_block_ids),
            "profile_data": json.dumps(profile_snapshot),
            "created_by_admin_id": admin_id,
        },
    )


def downgrade() -> None:
    # Keep seed data on downgrade to avoid accidental data loss.
    pass
