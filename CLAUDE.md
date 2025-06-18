# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the repository for "逐工一幅天文圖" (APOD Taigi), a Taiwanese translation of NASA's Astronomy Picture of the Day. It's a Hugo-based static website that provides daily astronomy content translated into Taiwanese (Taigi) language with podcast episodes.

## Common Commands

### Development Setup
```bash
make dev          # Install development dependencies and setup pre-commit hooks
pip install -e .  # Install the apod CLI tool
```

### Running the Site
```bash
make run          # Start Hugo development server on port 5566
```

### Content Management
```bash
apod update-podcasts      # Update podcast data in daily articles
apod update-vocabularies  # Generate vocabulary reference from all posts
apod shownotes DATE VOCAL # Generate podcast show notes (e.g., apod shownotes 20250610 "某某")
apod transcript DATE      # Generate transcript for a date
```

### Code Quality
```bash
make fmt                  # Run pre-commit formatting (black, isort, trailing whitespace, etc.)
pre-commit run --all-files  # Run all pre-commit hooks
```

## Architecture

### Content Structure
- **Daily Posts**: `content/daily/YYYY/MM/YYYYMMDD.md` - Daily APOD translations
- **Bonus Content**: `content/bonus/` - Additional astronomy articles and educational content
- **Content Format**: Each post contains multiple language versions (漢羅/POJ/KIP/English) and vocabulary tables

### Python CLI Tool (`apod/`)
- **RSS Integration**: `rss.py` handles podcast episode data
- **Content Processing**: `cli.py` provides utilities for content management and automation
- **Vocabulary Management**: Automatically extracts and consolidates astronomical terms from all posts

### Hugo Configuration
- **Theme**: Uses custom "newsroom" theme
- **Multilingual**: Traditional Chinese with Taiwanese language support
- **Podcasting**: Apple Podcast integration with episode embedding
- **Taxonomies**: Tags, categories, and vocals for content organization

### Automation
- **Scheduled Updates**: Daily cron jobs update podcast data (2 AM) and publish content (1 PM)
- **Content Processing**: Automated vocabulary extraction and podcast episode integration

## Content Creation Workflow

1. Create daily posts in `content/daily/YYYY/MM/YYYYMMDD.md`
2. Use the provided markdown template with frontmatter (title, date, tags, hero image, summary)
3. Include all language versions: 漢羅 (Han-lô), POJ, KIP, and English
4. Add vocabulary table with astronomical terms
5. Use `publishdate` for scheduled publishing

## Dependencies
- **Hugo**: Static site generator
- **Python**: CLI tools and automation (click, pendulum, beautifulsoup4, feedparser)
- **Pre-commit**: Code formatting and linting (black, isort)