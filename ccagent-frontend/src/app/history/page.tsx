// app/history/page.tsx
'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
// import { ScrollArea } from '@/components/ui/scroll-area'

export default function HistoryPage() {
    interface HistoryItem {
        session_id: string;
        company_name: string;
        date: string;
        industry: string;
        progress: number;
    }

    const [histories, setHistories] = useState<HistoryItem[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function fetchHistories() {
            try {
                const response = await fetch('http://localhost:8000/history')
                if (!response.ok) throw new Error('Failed to fetch history')
                const data = await response.json()
                setHistories(data)
            } catch (error) {
                console.error('Error fetching history:', error)
            } finally {
                setLoading(false)
            }
        }

        fetchHistories()
    }, [])

    return (
        <div className="container mx-auto py-10">
            <h1 className="text-3xl font-bold mb-6">Execution History</h1>

            {loading ? (
                <p>Loading history...</p>
            ) : (
                <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                    {histories.map((item) => (
                        <Card key={item.session_id}>
                            <CardHeader>
                                <CardTitle>{item.company_name}</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p><strong>Date:</strong> {new Date(item.date).toLocaleString()}</p>
                                <p><strong>Industry:</strong> {item.industry}</p>
                                <p><strong>Progress:</strong> {item.progress} tasks</p>
                                <a
                                    href={`/history/${item.session_id}`}
                                    className="text-blue-500 hover:underline"
                                >
                                    View Details
                                </a>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    )
}
