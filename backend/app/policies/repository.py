from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.policies.models import (
    PolicyModel, PolicyVersionModel, PolicyEvaluationModel, PolicyABTestModel, PolicyStatus
)

class PolicyRepository:
    """
    Data Access Repository for Policy domain ensuring multi-tenant isolation via organization_id.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_policy(self, policy: PolicyModel) -> PolicyModel:
        self.session.add(policy)
        await self.session.commit()
        await self.session.refresh(policy)
        return policy

    async def get_policy(self, policy_id: str, org_id: str) -> Optional[PolicyModel]:
        stmt = select(PolicyModel).where(
            PolicyModel.id == policy_id,
            PolicyModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_policy_by_agent(self, agent_name: str, org_id: str) -> Optional[PolicyModel]:
        stmt = select(PolicyModel).where(
            PolicyModel.agent_name == agent_name,
            PolicyModel.organization_id == org_id,
            PolicyModel.status == PolicyStatus.ACTIVE
        ).order_by(PolicyModel.updated_at.desc())
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_policies(self, org_id: str) -> List[PolicyModel]:
        stmt = select(PolicyModel).where(
            PolicyModel.organization_id == org_id
        ).order_by(PolicyModel.updated_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create_version(self, version: PolicyVersionModel) -> PolicyVersionModel:
        self.session.add(version)
        await self.session.commit()
        await self.session.refresh(version)
        return version

    async def get_version(self, policy_id: str, version_str: str, org_id: str) -> Optional[PolicyVersionModel]:
        stmt = select(PolicyVersionModel).where(
            PolicyVersionModel.policy_id == policy_id,
            PolicyVersionModel.version == version_str,
            PolicyVersionModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_versions(self, policy_id: str, org_id: str) -> List[PolicyVersionModel]:
        stmt = select(PolicyVersionModel).where(
            PolicyVersionModel.policy_id == policy_id,
            PolicyVersionModel.organization_id == org_id
        ).order_by(PolicyVersionModel.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_active_version(self, policy_id: str, org_id: str) -> Optional[PolicyVersionModel]:
        stmt = select(PolicyVersionModel).where(
            PolicyVersionModel.policy_id == policy_id,
            PolicyVersionModel.organization_id == org_id,
            PolicyVersionModel.status == PolicyStatus.ACTIVE
        ).order_by(PolicyVersionModel.created_at.desc())
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_evaluation(self, evaluation: PolicyEvaluationModel) -> PolicyEvaluationModel:
        self.session.add(evaluation)
        await self.session.commit()
        await self.session.refresh(evaluation)
        return evaluation

    async def list_evaluations(self, policy_id: str, org_id: str) -> List[PolicyEvaluationModel]:
        stmt = select(PolicyEvaluationModel).where(
            PolicyEvaluationModel.policy_id == policy_id,
            PolicyEvaluationModel.organization_id == org_id
        ).order_by(PolicyEvaluationModel.evaluated_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create_ab_test(self, ab_test: PolicyABTestModel) -> PolicyABTestModel:
        self.session.add(ab_test)
        await self.session.commit()
        await self.session.refresh(ab_test)
        return ab_test

    async def get_ab_test(self, ab_test_id: str, org_id: str) -> Optional[PolicyABTestModel]:
        stmt = select(PolicyABTestModel).where(
            PolicyABTestModel.id == ab_test_id,
            PolicyABTestModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
