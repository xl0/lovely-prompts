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


interface Data_LLMResponse extends ChatMessage, SQLRow {
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
    chat_messages?: ChatMessage[];
    completion_prompt?: string;
    responses?: Data_LLMResponse[];
};


interface WSMessage {
    id: number;
    prompt_id: number;
    action: "replace" | "append" | "delete";
    key: string;
    value: string;
}




