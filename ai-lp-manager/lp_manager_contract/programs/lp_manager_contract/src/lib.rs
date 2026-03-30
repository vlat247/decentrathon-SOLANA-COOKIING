use anchor_lang::prelude::*;

declare_id!("CSjDhZXoYAeSa8mtsy7xgSRVqq2Bbeb9jSwf9RP5QVN6");

#[program]
pub mod lp_manager_contract {
    use super::*;

    pub fn open_position(
        ctx: Context<OpenPosition>,
        pool_id: String,
        amount_usdc: u64,
    ) -> Result<()> {
        let pos = &mut ctx.accounts.position;
        pos.owner = ctx.accounts.owner.key();
        pos.pool_id = pool_id;
        pos.amount_usdc = amount_usdc;
        pos.last_action = "HOLD".to_string();
        pos.last_score = 5000;
        pos.total_actions = 0;
        pos.is_active = true;
        pos.last_updated = Clock::get()?.unix_timestamp;
        pos.bump = ctx.bumps.position;
        Ok(())
    }

    pub fn update_position(
        ctx: Context<UpdatePosition>,
        action: String,
        score: i64,
    ) -> Result<()> {
        let pos = &mut ctx.accounts.position;
        require!(pos.is_active, ErrorCode::PositionInactive);
        require!(pos.owner == ctx.accounts.owner.key(), ErrorCode::NotOwner);
        pos.last_action = action.clone();
        pos.last_score = score;
        pos.total_actions += 1;
        pos.last_updated = Clock::get()?.unix_timestamp;
        if action == "EXIT" {
            pos.is_active = false;
        }
        Ok(())
    }

    pub fn close_position(ctx: Context<ClosePosition>) -> Result<()> {
        let pos = &mut ctx.accounts.position;
        require!(pos.owner == ctx.accounts.owner.key(), ErrorCode::NotOwner);
        pos.is_active = false;
        Ok(())
    }
}

#[account]
pub struct LpPosition {
    pub owner: Pubkey,       // 32
    pub pool_id: String,     // 4 + 20
    pub amount_usdc: u64,    // 8
    pub last_action: String, // 4 + 10
    pub last_score: i64,     // 8
    pub total_actions: u64,  // 8
    pub is_active: bool,     // 1
    pub last_updated: i64,   // 8
    pub bump: u8,            // 1
}

impl LpPosition {
    pub const LEN: usize = 8 + 32 + 24 + 8 + 14 + 8 + 8 + 1 + 8 + 1;
}

#[derive(Accounts)]
#[instruction(pool_id: String)]
pub struct OpenPosition<'info> {
    #[account(
        init,
        payer = owner,
        space = LpPosition::LEN,
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
        bump = position.bump
    )]
    pub position: Account<'info, LpPosition>,
    pub owner: Signer<'info>,
}

#[derive(Accounts)]
pub struct ClosePosition<'info> {
    #[account(
        mut,
        seeds = [owner.key().as_ref(), position.pool_id.as_bytes()],
        bump = position.bump,
        close = owner
    )]
    pub position: Account<'info, LpPosition>,
    #[account(mut)]
    pub owner: Signer<'info>,
}

#[error_code]
pub enum ErrorCode {
    #[msg("You are not the owner of this position")]
    NotOwner,
    #[msg("Position is not active")]
    PositionInactive,
}
