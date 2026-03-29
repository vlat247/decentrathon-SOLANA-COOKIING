use anchor_lang::prelude::*;

declare_id!("CSjDhZXoYAeSa8mtsy7xgSRVqq2Bbeb9jSwf9RP5QVN6");

#[program]
pub mod lp_manager_contract {
    use super::*;

    pub fn open_position(ctx: Context<OpenPosition>, pool_id: String, amount_usdc: u64, strategy: String) -> Result<()> {
        let pos = &mut ctx.accounts.position;
        pos.owner = ctx.accounts.owner.key();
        pos.pool_id = pool_id;
        pos.amount_usdc = amount_usdc;
        pos.strategy = strategy;
        pos.last_action = "OPEN".to_string();
        pos.last_score = 0;
        pos.last_updated = Clock::get()?.unix_timestamp;
        pos.total_actions = 0;
        pos.is_active = true;
        pos.bump = ctx.bumps.position;

        emit!(PositionOpened {
            owner: pos.owner,
            pool_id: pos.pool_id.clone(),
            amount_usdc: pos.amount_usdc,
            timestamp: pos.last_updated,
        });

        Ok(())
    }

    pub fn update_position(ctx: Context<UpdatePosition>, action: String, score: i64) -> Result<()> {
        let pos = &mut ctx.accounts.position;
        require!(pos.is_active, ErrorCode::PositionInactive);
        
        pos.last_action = action.clone();
        pos.last_score = score;
        pos.last_updated = Clock::get()?.unix_timestamp;
        pos.total_actions += 1;

        if action == "EXIT" {
            pos.is_active = false;
        }

        emit!(PositionUpdated {
            owner: pos.owner,
            pool_id: pos.pool_id.clone(),
            action,
            score,
            timestamp: pos.last_updated,
        });

        Ok(())
    }

    pub fn close_position(ctx: Context<ClosePosition>) -> Result<()> {
        let pos = &mut ctx.accounts.position;
        pos.is_active = false;
        
        emit!(PositionClosed {
            owner: pos.owner,
            pool_id: pos.pool_id.clone(),
            timestamp: Clock::get()?.unix_timestamp,
        });

        Ok(())
    }
}

#[derive(Accounts)]
#[instruction(pool_id: String)]
pub struct OpenPosition<'info> {
    #[account(
        init,
        payer = owner,
        space = 8 + 32 + (4 + 20) + 8 + (4 + 10) + (4 + 10) + 8 + 8 + 8 + 1 + 1,
        seeds = [owner.key().as_ref(), pool_id.as_bytes()],
        bump
    )]
    pub position: Account<'info, LpPosition>,
    #[account(mut)]
    pub owner: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct UpdatePosition<'info> {
    #[account(
        mut,
        seeds = [owner.key().as_ref(), position.pool_id.as_bytes()],
        bump = position.bump,
        has_one = owner @ ErrorCode::NotOwner
    )]
    pub position: Account<'info, LpPosition>,
    pub owner: Signer<'info>,
}

#[derive(Accounts)]
pub struct ClosePosition<'info> {
    #[account(
        mut,
        close = owner,
        seeds = [owner.key().as_ref(), position.pool_id.as_bytes()],
        bump = position.bump,
        has_one = owner @ ErrorCode::NotOwner
    )]
    pub position: Account<'info, LpPosition>,
    #[account(mut)]
    pub owner: Signer<'info>,
}

#[account]
pub struct LpPosition {
    pub owner: Pubkey,
    pub pool_id: String,
    pub amount_usdc: u64,
    pub strategy: String,
    pub last_action: String,
    pub last_score: i64,
    pub last_updated: i64,
    pub total_actions: u64,
    pub is_active: bool,
    pub bump: u8,
}

#[event]
pub struct PositionOpened {
    pub owner: Pubkey,
    pub pool_id: String,
    pub amount_usdc: u64,
    pub timestamp: i64,
}

#[event]
pub struct PositionUpdated {
    pub owner: Pubkey,
    pub pool_id: String,
    pub action: String,
    pub score: i64,
    pub timestamp: i64,
}

#[event]
pub struct PositionClosed {
    pub owner: Pubkey,
    pub pool_id: String,
    pub timestamp: i64,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Not position owner")]
    NotOwner,
    #[msg("Position is currently inactive")]
    PositionInactive,
    #[msg("Invalid action string")]
    InvalidAction,
}
