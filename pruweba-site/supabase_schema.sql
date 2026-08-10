-- Client Portal schema (matches the LIVE database, verified by introspection
-- against project ukbcywxtnyizkmgjyhdt on 2026-08-11).
--
-- NOTE: both tables already exist in production. This file is idempotent and
-- documents the real shape; running it will not clobber existing data.

create extension if not exists "pgcrypto";

create table if not exists public.client_projects (
    id                  uuid primary key default gen_random_uuid(),
    client_name         text not null unique,
    assigned_user_email text,
    problem_statement   text,
    success_criteria    text,
    constraints         text,
    current_phase       int  not null default 1,
    created_at          timestamptz not null default now()
);

-- AUTH MIGRATION: links a Supabase Auth user to their project.
-- Run this if client_projects already exists (it does, in production).
alter table public.client_projects
    add column if not exists assigned_user_email text;

create unique index if not exists client_projects_assigned_email_idx
    on public.client_projects (lower(assigned_user_email))
    where assigned_user_email is not null;

create table if not exists public.project_milestones (
    id            uuid primary key default gen_random_uuid(),
    project_id    uuid not null references public.client_projects(id) on delete cascade,
    phase_id      int  not null,
    name          text not null,
    status        text not null default 'pending'
                  check (status in ('pending', 'active', 'done')),
    client_signed boolean not null default false,
    proof_hash    text,
    completed_at  timestamptz,
    created_at    timestamptz not null default now(),
    unique (project_id, phase_id)
);

create index if not exists project_milestones_project_idx
    on public.project_milestones (project_id, phase_id);

-- Proof hashes are append-only: once sealed, a hash may never be rewritten.
create or replace function public.guard_proof_immutable()
returns trigger language plpgsql as $$
begin
    if old.proof_hash is not null and new.proof_hash is distinct from old.proof_hash then
        raise exception 'proof_hash is immutable once sealed (milestone %)', old.name;
    end if;
    return new;
end $$;

drop trigger if exists project_milestones_proof_guard on public.project_milestones;
create trigger project_milestones_proof_guard
    before update on public.project_milestones
    for each row execute function public.guard_proof_immutable();

-- RLS: reads are public, writes only via the service_role key used by /api/portal.
alter table public.client_projects    enable row level security;
alter table public.project_milestones enable row level security;

drop policy if exists client_projects_read on public.client_projects;
create policy client_projects_read
    on public.client_projects for select to anon, authenticated using (true);

drop policy if exists project_milestones_read on public.project_milestones;
create policy project_milestones_read
    on public.project_milestones for select to anon, authenticated using (true);

-- Seed (already applied via tests/seed.py):
--   insert into public.client_projects (client_name, problem_statement, current_phase)
--   values ('Paydora_Payments', 'Payment reconciliation platform delivery', 1);
--   then 5 rows in project_milestones with phase_id 1..5.
