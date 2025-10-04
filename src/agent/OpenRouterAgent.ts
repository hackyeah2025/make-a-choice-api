export interface OpenRouterMessage {
    role: 'system' | 'user' | 'assistant';
    content: string;
}

export interface OpenRouterRequest {
    model: string;
    messages: OpenRouterMessage[];
    max_tokens?: number;
    temperature?: number;
    top_p?: number;
    frequency_penalty?: number;
    presence_penalty?: number;
    stream?: boolean;
}

export interface OpenRouterResponse {
    id: string;
    object: string;
    created: number;
    model: string;
    choices: Array<{
        index: number;
        message: {
            role: string;
            content: string;
        };
        finish_reason: string;
    }>;
    usage: {
        prompt_tokens: number;
        completion_tokens: number;
        total_tokens: number;
    };
}

export abstract class OpenRouterAgent {
    protected apiKey: string;
    protected baseUrl: string = 'https://openrouter.ai/api/v1';
    protected model: string;
    protected systemPrompt: string;
    protected maxTokens: number;
    protected temperature: number;

    constructor(
        apiKey?: string,
        model: string = 'openai/gpt-3.5-turbo',
        maxTokens: number = 1000,
        temperature: number = 0.7
    ) {
        // Use provided API key or get it from environment variables
        this.apiKey = apiKey || process.env.OPENROUTER_API_KEY || '';
        if (!this.apiKey) {
            throw new Error('OpenRouter API key not provided. Set OPENROUTER_API_KEY in your .env file.');
        }

        this.model = model;
        this.maxTokens = maxTokens;
        this.temperature = temperature;
        this.systemPrompt = this.getSystemPrompt();
    }

    /**
     * Abstract method to be implemented by child classes
     * Returns the system prompt for the specific agent
     */
    protected abstract getSystemPrompt(): string;

    /**
     * Send a message to the OpenRouter API
     */
    protected async sendMessage(
        userMessage: string,
        additionalMessages: OpenRouterMessage[] = []
    ): Promise<string> {
        try {
            const messages: OpenRouterMessage[] = [
                { role: 'system', content: this.systemPrompt },
                ...additionalMessages,
                { role: 'user', content: userMessage }
            ];

            const requestData: OpenRouterRequest = {
                model: this.model,
                messages,
                max_tokens: this.maxTokens,
                temperature: this.temperature
            };

            const response = await fetch(`${this.baseUrl}/chat/completions`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json',
                    'HTTP-Referer': process.env.YOUR_SITE_URL || 'http://localhost:3000',
                    'X-Title': process.env.YOUR_SITE_NAME || 'Make a Choice API'
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`OpenRouter API Error: ${errorData.error || response.statusText}`);
            }

            const data: OpenRouterResponse = await response.json();

            if (data.choices && data.choices.length > 0) {
                return data.choices[0].message.content;
            } else {
                throw new Error('No response from OpenRouter API');
            }
        } catch (error) {
            if (error instanceof Error) {
                throw new Error(`OpenRouter API Error: ${error.message}`);
            }
            throw new Error('Unknown error occurred while calling OpenRouter API');
        }
    }

    /**
     * Process a user request - to be implemented by child classes
     */
    public abstract process(input: string, context?: any): Promise<string>;

    /**
     * Get agent information
     */
    public getInfo(): { name: string; model: string; systemPrompt: string } {
        return {
            name: this.constructor.name,
            model: this.model,
            systemPrompt: this.systemPrompt
        };
    }
}
