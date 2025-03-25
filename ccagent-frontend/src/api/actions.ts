// app/actions.ts
'use server'

import { z } from 'zod'
import { revalidatePath } from 'next/cache'

const formSchema = z.object({
    csv_file: z.string().min(1),
    company_name: z.string().min(1),
    industry: z.string().min(1),
    brand_guidelines: z.string().min(1),
    brand_voice: z.string().min(1),
    current_date: z.string().min(1),
})

export type FormData = z.infer<typeof formSchema>
export type TaskProgress = {
    agent: string;
    task: string;
    status: 'in_progress' | 'completed';
    start_time: string;
    end_time: string | null;
    duration: number | null;
}

export type StreamUpdate = {
    type: 'log' | 'progress' | 'output';
    content: string;
    progress?: number;
    remainingTime?: number;
    agent?: string;
    task?: string;
}

export async function executeCrewAction(formData: FormData): Promise<ReadableStream<Uint8Array>> {
    // Validate the form data
    const validatedFields = formSchema.safeParse(formData)

    if (!validatedFields.success) {
        throw new Error('Invalid form data')
    }

    // Create a TransformStream to handle the streaming response
    const { readable, writable } = new TransformStream()

    // Process the request in the background
    processRequest(validatedFields.data, writable).catch((error) => {
        console.error('Error processing request:', error)
    })

    // Return the readable stream to the client
    return readable
}

async function processRequest(data: FormData, writable: WritableStream<Uint8Array>) {
    const writer = writable.getWriter()
    const encoder = new TextEncoder()

    try {
        // Make the actual fetch request to your backend API
        const response = await fetch('http://localhost:8000/execute_crew', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        // Stream the response back to the client
        const reader = response.body?.getReader()
        if (!reader) {
            throw new Error('Response body is null')
        }

        while (true) {
            const { done, value } = await reader.read()

            if (done) break

            // Pass the chunks directly to the client
            await writer.write(value)
        }

        // Revalidate the page to reflect any changes
        revalidatePath('/')
    } catch (error) {
        // Send error message to the client
        const errorMessage = `Error: ${error instanceof Error ? error.message : String(error)}`
        await writer.write(encoder.encode(errorMessage))
    } finally {
        await writer.close()
    }
}

export async function fetchHistory(sessionId?: string) {
    try {
        const url = sessionId
            ? `http://localhost:8000/history/${sessionId}`
            : 'http://localhost:8000/history';

        const response = await fetch(url, { next: { revalidate: 0 } });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching history:', error);
        throw error;
    }
}
