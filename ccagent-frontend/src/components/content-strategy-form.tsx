"use client"

import { useState, useRef, useEffect } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { format } from 'date-fns'
import { marked } from 'marked'

import { Button } from '@/components/ui/button'
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Loader2 } from 'lucide-react'
import { executeCrewAction, FormData } from '@/api/actions'
import { Progress } from '@/components/ui/progress'

const formSchema = z.object({
    csv_file: z.string().min(1, { message: 'CSV file is required' }),
    company_name: z.string().min(1, { message: 'Company name is required' }),
    industry: z.string().min(1, { message: 'Industry is required' }),
    brand_guidelines: z.string().min(1, { message: 'Brand guidelines are required' }),
    brand_voice: z.string().min(1, { message: 'Brand voice is required' }),
    current_date: z.string().min(1, { message: 'Current date is required' }),
})

interface ContentStrategyFormProps {
    onUpdate: (update: string) => void
    onOutput: (content: string) => void
    onSessionId?: (sessionId: string) => void
}

export function ContentStrategyForm({ onUpdate, onOutput, onSessionId }: ContentStrategyFormProps) {
    const [isLoading, setIsLoading] = useState(false)
    const [progress, setProgress] = useState(0)
    const [currentAgent, setCurrentAgent] = useState<string>('')
    const [currentTask, setCurrentTask] = useState<string>('')
    const [remainingTime, setRemainingTime] = useState<number | null>(null)
    const abortControllerRef = useRef<AbortController | null>(null)

    const form = useForm<FormData>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            csv_file: 'data.csv',
            company_name: 'convogrid.ai',
            industry: 'Conversation Design and Marketing and Content Creation',
            brand_guidelines: 'modern, youthful, eco-conscious',
            brand_voice: 'casual yet authoritative',
            current_date: format(new Date(), 'yyyy MMMM dd'),
        },
    })

    useEffect(() => {
        // Cleanup function to abort any ongoing requests when component unmounts
        return () => {
            if (abortControllerRef.current) {
                abortControllerRef.current.abort()
            }
        }
    }, [])

    async function onSubmit(data: FormData) {
        setIsLoading(true)
        setProgress(0)

        // Create a new AbortController for this request
        abortControllerRef.current = new AbortController()

        try {
            // Call the server action
            const stream = await executeCrewAction(data)

            // Create a reader from the stream
            const reader = stream.getReader()
            const decoder = new TextDecoder()
            let markdownText = ''
            let sessionIdFound = false

            while (true) {
                const { done, value } = await reader.read()

                if (done) break

                const text = decoder.decode(value)

                // Check for session ID in the completion message
                if (!sessionIdFound && text.includes("Session ID:")) {
                    const match = text.match(/Session ID: ([a-f0-9-]+)/i)
                    if (match && match[1] && onSessionId) {
                        sessionIdFound = true
                        onSessionId(match[1])
                    }
                }

                // Parse progress information
                if (text.includes("Progress:")) {
                    const progressMatch = text.match(/Progress: (\d+\.\d+)%/)
                    if (progressMatch && progressMatch[1]) {
                        setProgress(parseFloat(progressMatch[1]))
                    }

                    // Extract remaining time if available
                    const timeMatch = text.match(/Estimated time remaining: (\d+) seconds/)
                    if (timeMatch && timeMatch[1]) {
                        setRemainingTime(parseInt(timeMatch[1]))
                    }

                    // Extract agent and task information
                    const agentMatch = text.match(/Agent: ([^-]+) - Task: ([^-]+)/)
                    if (agentMatch && agentMatch[1] && agentMatch[2]) {
                        setCurrentAgent(agentMatch[1].trim())
                        setCurrentTask(agentMatch[2].trim())
                    }
                }

                if (text.startsWith("Agent:") || text.includes("Progress:") || text.includes("Completed:")) {
                    onUpdate(text)
                } else if (text.includes("# Content Strategy Plan")) {
                    // This is the start of markdown output
                    markdownText = text
                    const parsedMarkdown = await marked.parse(markdownText)
                    onOutput(parsedMarkdown)
                } else if (markdownText) {
                    // Append to existing markdown
                    markdownText += text
                    
                }
            }
        } catch (error) {
            console.error('Error:', error)
            onUpdate(`Error: ${error instanceof Error ? error.message : String(error)}`)
        } finally {
            setIsLoading(false)
            abortControllerRef.current = null
        }
    }

    return (
        <div className="space-y-6">
            {isLoading && (
                <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                        <span>{currentAgent ? `${currentAgent}` : 'Processing'}</span>
                        <span>{currentTask}</span>
                    </div>
                    <Progress value={progress} className="h-2" />
                    <div className="flex justify-between text-xs text-muted-foreground">
                        <span>{progress.toFixed(1)}% complete</span>
                        {remainingTime !== null && (
                            <span>~{remainingTime} seconds remaining</span>
                        )}
                    </div>
                </div>
            )}

            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    <FormField
                        control={form.control}
                        name="csv_file"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>CSV File</FormLabel>
                                <FormControl>
                                    <Input {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="company_name"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Company Name</FormLabel>
                                <FormControl>
                                    <Input {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="industry"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Industry</FormLabel>
                                <FormControl>
                                    <Input {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="brand_guidelines"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Brand Guidelines</FormLabel>
                                <FormControl>
                                    <Input {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="brand_voice"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Brand Voice</FormLabel>
                                <FormControl>
                                    <Input {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="current_date"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Current Date</FormLabel>
                                <FormControl>
                                    <Input {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <Button type="submit" className="w-full" disabled={isLoading}>
                        {isLoading ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Processing...
                            </>
                        ) : (
                            'Execute Crew'
                        )}
                    </Button>
                </form>
            </Form>
        </div>
    )
}
