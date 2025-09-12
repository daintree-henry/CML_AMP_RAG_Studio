/*
 * CLOUDERA APPLIED MACHINE LEARNING PROTOTYPE (AMP)
 * (C) Cloudera, Inc. 2025
 * All rights reserved.
 *
 * Applicable Open Source License: Apache 2.0
 *
 * NOTE: Cloudera open source products are modular software products
 * made up of hundreds of individual components, each of which was
 * individually copyrighted.  Each Cloudera open source product is a
 * collective work under U.S. Copyright Law. Your license to use the
 * collective work is as provided in your written agreement with
 * Cloudera.  Used apart from the collective work, this file is
 * licensed for your use pursuant to the open source license
 * identified above.
 *
 * This code is provided to you pursuant a written agreement with
 * (i) Cloudera, Inc. or (ii) a third-party authorized to distribute
 * this code. If you do not have a written agreement with Cloudera nor
 * with an authorized and properly licensed third party, you do not
 * have any rights to access nor to use this code.
 *
 * Absent a written agreement with Cloudera, Inc. ("Cloudera") to the
 * contrary, A) CLOUDERA PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY
 * KIND; (B) CLOUDERA DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED
 * WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT LIMITED TO
 * IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND
 * FITNESS FOR A PARTICULAR PURPOSE; (C) CLOUDERA IS NOT LIABLE TO YOU,
 * AND WILL NOT DEFEND, INDEMNIFY, NOR HOLD YOU HARMLESS FOR ANY CLAIMS
 * ARISING FROM OR RELATED TO THE CODE; AND (D)WITH RESPECT TO YOUR EXERCISE
 * OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, CLOUDERA IS NOT LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR
 * CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO, DAMAGES
 * RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF
 * BUSINESS ADVANTAGE OR UNAVAILABILITY, OR LOSS OR CORRUPTION OF
 * DATA.
 */

import {
  Button,
  Card,
  Flex,
  Form,
  Input,
  Layout,
  Typography,
  Space,
} from "antd";
import { PlusOutlined, DeleteOutlined } from "@ant-design/icons";

const ChatSettingsPage = () => {
  const [form] = Form.useForm();

  return (
    <Layout
      style={{
        alignItems: "center",
        width: "100%",
        paddingLeft: 60,
      }}
    >
      <Flex vertical gap={20} style={{ width: "100%", maxWidth: 800 }}>
        <Typography.Title level={3}>(Beta) Chat Settings</Typography.Title>
        <Typography.Paragraph>
          Manage default chat settings that will be applied to the chat room.
          <br />- Studio Name: Main name shown when entering the chat
          <br />- Dummy Questions: List of suggested questions shown at the
          start
          <br />- System Prompt: Default prompt applied to the conversation
        </Typography.Paragraph>

        <Card>
          <Form
            form={form}
            layout="vertical"
            initialValues={{
              studioName: "",
              dummyQuestions: [],
              systemPrompt: "",
            }}
          >
            <Form.Item
              label="Studio Name"
              name="studioName"
              rules={[{ required: true, message: "Please enter studio name" }]}
              extra="Main name displayed when entering the chat"
            >
              <Input placeholder="e.g. RAG Studio" />
            </Form.Item>

            <Form.Item
              label="Dummy Questions"
              required
              extra="List of suggested questions displayed when entering the chat"
            >
              <Form.List name="dummyQuestions">
                {(fields, { add, remove }) => (
                  <>
                    {fields.map((field, index) => (
                      <Space
                        key={field.key}
                        style={{ display: "flex", marginBottom: 8 }}
                        align="baseline"
                      >
                        <Form.Item
                          {...field}
                          rules={[{
                            required: true,
                            message: "Please enter a dummy question",
                          }]}
                        >
                          <Input placeholder={`Dummy question ${index + 1}`} />
                        </Form.Item>
                        <DeleteOutlined
                          onClick={() => remove(field.name)}
                          style={{ color: "red" }}
                        />
                      </Space>
                    ))}
                    <Button
                      type="dashed"
                      onClick={() => add()}
                      block
                      icon={<PlusOutlined />}
                    >
                      Add Question
                    </Button>
                  </>
                )}
              </Form.List>
            </Form.Item>

            <Form.Item
              label="System Prompt"
              name="systemPrompt"
              rules={[{ required: true, message: "Please enter system prompt" }]}
              extra="Default system prompt applied to the chat"
            >
              <Input.TextArea
                rows={6}
                placeholder="e.g. You are a helpful AI assistant..."
              />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit">
                Save Settings
              </Button>
            </Form.Item>
          </Form>
        </Card>
      </Flex>
    </Layout>
  );
};

export default ChatSettingsPage;
