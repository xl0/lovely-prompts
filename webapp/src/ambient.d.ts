interface Chunk {
    title?: string;
    comment?: string;
};

interface SQLRow {
    id: number;
    created: string;
    updated: string;
};


interface ChatMessage extends Chunk {
    role?: string;
    content?: string;
};


interface Data_ChatResponse extends Chunk, SQLRow {
    prompt_id?: number;
    response: ChatMessage;
    tok_in?: number;
    tok_out?: number;
    tok_max?: number;
    model?: string;
    temperature?: number;
    provider?: string;
    meta?: Record<string, unknown>;
}

interface Data_ChatPrompt extends Chunk, SQLRow {
    messages?: ChatMessage[];
    responses?: Data_ChatResponse[];
};
