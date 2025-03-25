# PC Builder Technical Documentation

## Project Overview

PC Builder is a Next.js web application designed to help users build custom PC configurations. The application provides two distinct user experiences:

1. **Skilled Builder**: A streamlined interface for experienced users to directly select PC components with compatibility checks.
2. **Beginner Builder**: An interactive chat-based interface that guides novice users through component selection based on their needs and budget.

## Technology Stack

- **Frontend**: Next.js 15.1.6 with React 19
- **Styling**: Tailwind CSS
- **Database**: PostgreSQL (via pg package)
- **AI Integration**: Ollama for the beginner builder chat interface
- **Markdown Rendering**: react-markdown for formatted chat responses

## Project Structure

```
pc-builder/
├── .next/                 # Next.js build output
├── .git/                  # Git repository
├── db/                    # Database files
├── node_modules/          # Node.js dependencies
├── public/                # Static assets
├── src/                   # Source code
│   ├── app/               # Next.js app router
│   │   ├── api/           # API routes
│   │   ├── beginner/      # Beginner builder page
│   │   ├── skilled/       # Skilled builder page
│   │   ├── favicon.ico    # Site favicon
│   │   ├── globals.css    # Global CSS
│   │   ├── layout.tsx     # Root layout
│   │   └── page.tsx       # Home page
│   ├── components/        # React components
│   │   ├── BeginnerBuilder.tsx  # Chat interface for beginners
│   │   ├── Navigation.tsx       # Site navigation
│   │   ├── SkilledBuilder.tsx   # Component selector for skilled users
│   │   └── StreamingText.tsx    # Text streaming component for chat
│   ├── data/              # Static data files
│   ├── db_setup/          # Database initialization
│   │   ├── import_data.py      # Script to import data into database
│   │   ├── mod_columns.sql     # SQL to modify database columns
│   │   ├── mod_data.py         # Script to modify imported data
│   │   ├── schema.sql          # Database schema definition
│   │   └── schema_only.sql     # Schema without data
│   └── lib/               # Utility functions and libraries
│       ├── ollama.ts      # AI chat integration
│       └── parts-data.ts  # PC parts data handling
├── .env                   # Environment variables
├── package.json           # Node.js dependencies and scripts
├── tailwind.config.ts     # Tailwind CSS configuration
└── tsconfig.json          # TypeScript configuration
```

## Data Model

The application uses a PostgreSQL database with the following main tables:

1. **cpu**: CPU components with specifications (core count, clock speed, etc.)
2. **motherboard**: Motherboard components with specifications (socket, form factor, etc.)
3. **memory**: RAM modules with specifications (speed, latency, etc.)
4. **storage**: Storage devices with specifications (capacity, type, interface, etc.)
5. **video_card**: GPU components with specifications (memory, clock speed, etc.)
6. **case_enclosure**: PC cases with specifications (type, color, size, etc.)
7. **power_supply**: PSU components with specifications (wattage, efficiency, etc.)
8. **cpu_cooler**: CPU cooling solutions with specifications (RPM, noise level, etc.)

Additionally, compatibility tables define relationships between components:

- **cpu_motherboard_compatibility**: Links compatible CPUs and motherboards
- **case_motherboard_compatibility**: Links compatible cases and motherboards
- **memory_motherboard_compatibility**: Links compatible memory and motherboards

## Component Details

### SkilledBuilder Component

- Implements a step-by-step interface for selecting PC components
- Maintains component selection state and handles compatibility filtering
- Dynamically fetches compatible parts based on previous selections
- Components are selected in this order: CPU, Motherboard, CPU Cooler, GPU, Case, PSU, RAM, Storage
- Provides part search functionality and displays pricing information

### BeginnerBuilder Component

- Implements a chat-based interface for guiding users through PC building
- Uses Ollama's AI model (qwen2.5:14b) to process user inputs and provide recommendations
- Renders markdown-formatted responses with the react-markdown library
- Streams AI responses for a better user experience

### Navigation Component

- Provides site-wide navigation

### StreamingText Component

- Displays streaming text with a typing effect for the AI chat interface

## API Routes

The application provides RESTful API endpoints under `/api/parts/[component]` that:

1. Return lists of components filtered by compatibility
2. Accept query parameters for filtering (e.g., cpu_id, mobo_id, gpu_id)
3. Format and return component details and pricing information

## User Flows

### Skilled Builder Flow:

1. User selects a CPU from the available options
2. Application filters motherboards compatible with the selected CPU
3. User selects a motherboard
4. Process continues with each component selection filtering subsequent options
5. User completes the build by selecting all components
6. Total price is calculated and displayed

### Beginner Builder Flow:

1. User opens the beginner interface
2. AI assistant asks questions about budget, needs, and use cases
3. Based on responses, the AI recommends a complete PC build
4. The build recommendation includes all components and pricing
5. The assistant can answer follow-up questions and provide explanations

## Database Initialization

The database is initialized using SQL scripts in the `db_setup` directory:

1. `schema.sql` defines the table structure
2. `import_data.py` imports component data into the database
3. `mod_data.py` modifies imported data for consistency
4. `mod_columns.sql` adds or modifies columns in the database schema

## AI Integration

The application integrates with Ollama to provide AI-assisted building advice:

- The AI uses a system prompt that defines its role and response format
- It's configured to ask questions to understand user needs
- The AI provides formatted recommendations with component lists and pricing
- The chat interface streams responses for a better user experience

## Development Setup

The project uses:

- Next.js with turbopack for development
- TypeScript for type safety
- ESLint for code quality
- Tailwind CSS for styling
- PostgreSQL for data storage

To run the project locally:

1. Install dependencies: `npm install`
2. Set up the PostgreSQL database
3. Run database setup scripts
4. Start the development server: `npm run dev`

## Performance Considerations

- Database indexes are created for better query performance
- Component data is fetched dynamically based on compatibility requirements
- The UI is responsive and works across device sizes

## Security

- Database queries are parameterized to prevent SQL injection
- The AI assistant is configured to only respond to PC building related queries
- Environment variables are used for sensitive configuration

## Future Enhancements

Potential areas for improvement:

1. Expand component database with more options
2. Add performance prediction for selected builds
3. Implement build saving and sharing functionality
4. Add visualization of the completed PC build
5. Enhance compatibility checking with more detailed specifications
