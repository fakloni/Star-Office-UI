# Phase 6 验收单（资产读取面收敛 + 限流内存稳定）

本阶段目标（非破坏）：
- 进一步收敛资产侧读接口暴露面（可开关）
- 防止限流桶无限增长（内存稳定性）

## 已做内容
1) 新增可选开关：`STAR_OFFICE_ASSET_READ_AUTH_ENABLED=false`
- 开启后，`/assets/list` 与 `/assets/template.zip` 需要认证（抽屉会话或 Bearer）
- 默认关闭，保持现网兼容

2) 限流桶清理优化
- 写接口限流桶超过阈值时自动清理过期项，避免长时间内存增长

3) 配置/检查同步
- `.env.example` 增加开关说明
- `scripts/security_check.py` 在生产模式下给出提示

## 线上验收
- 不改环境变量时，功能应保持原样
- 若后续你开启开关，未认证访问 `/assets/list` 应 401

## 回滚
- 环境层：将 `STAR_OFFICE_ASSET_READ_AUTH_ENABLED=false`
- 代码层：`git revert <phase6_commit>`
