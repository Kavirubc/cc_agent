'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'

export default function HistoryDetailPage() {
    const { sessionId } = useParams()
    const [historyData, setHistoryData] = useState<any>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function fetchHistoryDetail() {
            try {
                const response = await fetch(`http://localhost:8000/history/${sessionId}`)
                if (!response.ok) throw new Error('Failed to fetch history details')
                const data = await response.json()
                setHistoryData(data)
            } catch (error) {
                console.error('Error fetching history details:', error)
            } finally {
                setLoading(false)
            }
        }

        if (sessionId) {
            fetchHistoryDetail()
        }
    }, [sessionId])

    if (loading) return <p>Loading history details...</p>
    if (!historyData) return <p>History not found</p>

    return (
        <div className="container mx-auto py-10">
            <h1 className="text-3xl font-bold mb-6">History Details</h1>

            <Tabs defaultValue="output">
                <TabsList>
                    <TabsTrigger value="output">Output</TabsTrigger>
                    <TabsTrigger value="logs">Logs</TabsTrigger>
                    <TabsTrigger value="progress">Task Progress</TabsTrigger>
                </TabsList>

                <TabsContent value="output">
                    <Card>
                        <CardHeader>
                            <CardTitle>Output</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ScrollArea className="h-[500px]">
                                <div
                                    className="prose prose-sm max-w-none dark:prose-invert"
                                    dangerouslySetInnerHTML={{ __html: historyData.markdown_output || '' }}
                                />
                            </ScrollArea>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="logs">
                    <Card>
                        <CardHeader>
                            <CardTitle>Execution Logs</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ScrollArea className="h-[500px]">
                                <pre className="text-sm whitespace-pre-wrap">{historyData.logs || ''}</pre>
                            </ScrollArea>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="progress">
                    <Card>
                        <CardHeader>
                            <CardTitle>Task Progress</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ScrollArea className="h-[500px]">
                                <div className="space-y-4">
                                    {Array.isArray(historyData.task_progress) ? (
                                        historyData.task_progress.map((task, index) => (
                                            <div key={index} className="border p-4 rounded-md">
                                                <div className="font-medium">{task.agent}</div>
                                                <div className="text-sm">{task.task}</div>
                                                <div className="text-sm text-muted-foreground">
                                                    Status: {task.status}
                                                </div>
                                                {task.duration !== undefined && (
                                                    <div className="text-xs">
                                                        Duration: {task.duration.toFixed(2)}s
                                                    </div>
                                                )}
                                            </div>
                                        ))
                                    ) : (
                                        <p>No task progress data available</p>
                                    )}
                                </div>
                            </ScrollArea>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}
