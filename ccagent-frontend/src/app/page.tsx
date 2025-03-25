"use client"

import { useState } from 'react'
import { ContentStrategyForm } from '@/components/content-strategy-form'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function ContentStrategyPage() {
  const [updates, setUpdates] = useState<string[]>([])
  const [output, setOutput] = useState<string>('')

  const handleUpdates = (update: string) => {
    setUpdates(prev => [...prev, update])
  }

  const handleOutput = (content: string) => {
    setOutput(content)
  }

  return (
    <div className="container mx-auto py-10 space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Content Strategy Crew</h1>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Strategy Configuration</CardTitle>
          </CardHeader>
          <CardContent>
            <ContentStrategyForm onUpdate={handleUpdates} onOutput={handleOutput} />
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Tabs defaultValue="updates">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="updates">Updates</TabsTrigger>
              <TabsTrigger value="output">Output</TabsTrigger>
            </TabsList>

            <TabsContent value="updates">
              <Card>
                <CardHeader>
                  <CardTitle>Updates</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[500px]">
                    <div className="space-y-2">
                      {updates.length > 0 ? (
                        updates.map((update, index) => (
                          <p key={index} className="text-sm">{update}</p>
                        ))
                      ) : (
                        <p className="text-sm text-muted-foreground">No updates yet</p>
                      )}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="output">
              <Card>
                <CardHeader>
                  <CardTitle>Output</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[500px]">
                    {output ? (
                      <div className="prose prose-sm max-w-none" dangerouslySetInnerHTML={{ __html: output }} />
                    ) : (
                      <p className="text-sm text-muted-foreground">No output yet</p>
                    )}
                  </ScrollArea>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
