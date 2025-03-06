-- Create categories table
create table if not exists categories (
    id bigint primary key generated always as identity,
    title text not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    clues_count integer default 0 not null
);

-- Create clues table
create table if not exists clues (
    id bigint primary key generated always as identity,
    answer text not null,
    question text not null,
    value integer,
    airdate timestamp with time zone not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    category_id bigint references categories(id) not null,
    game_id bigint,
    invalid_count integer
);

-- Enable Row Level Security
alter table categories enable row level security;
alter table clues enable row level security;

-- Create policies for public read access
create policy "Public can read categories"
    on categories for select
    to anon
    using (true);

create policy "Public can read clues"
    on clues for select
    to anon
    using (true);

-- Create indexes for better performance
create index if not exists idx_clues_category_id on clues(category_id);
create index if not exists idx_categories_title on categories(title); 