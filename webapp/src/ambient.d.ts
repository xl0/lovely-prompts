interface Chunk {
    title?: string;
    comment?: string;
};

interface SQLRow {
    id: string;
    created: string;
    updated: string;
};


interface ChatMessage extends Chunk {
    role?: string;
    content?: string;
};


interface Data_LLMResponse extends ChatMessage, SQLRow {
    [key: string]: any;
    prompt_id?: number;
    stop_reason?: string;
    tok_in?: number;
    tok_out?: number;
    tok_max?: number;
    model?: string;
    temperature?: number;
    provider?: string;
    meta?: Record<string, unknown>;
}

interface Data_LLMPrompt extends Chunk, SQLRow {
    prompt?: ChatMessage[];
    completion_prompt?: string;
    responses?: Data_LLMResponse[];
};

interface WSMessage {
    id: string;
    prompt_id: string;
    action: "replace" | "append" | "delete";
    key: string;
    value: string;
}


