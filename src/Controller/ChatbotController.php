<?php

namespace App\Controller;

use App\Entity\ChatMessage;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Contracts\HttpClient\HttpClientInterface;

class ChatbotController extends AbstractController
{
    private $httpClient;

    public function __construct(HttpClientInterface $httpClient)
    {
        $this->httpClient = $httpClient;
    }
    #[Route('/chatbot', name: 'app_chatbot')]
    public function index(): Response
    {
        return $this->render('chatbot/index.html.twig', [
            'controller_name' => 'ChatbotController',
        ]);
    }
    /**
     * @Route("/chatbot/response", name="chatbot_response", methods={"POST"})
     */
    public function getResponse(Request $request, EntityManagerInterface $entityManager): JsonResponse
    {
        // Decode the JSON payload
        $content = json_decode($request->getContent(), true);

        if (!isset($content['question']) || empty($content['question'])) {
            return new JsonResponse(['error' => 'No question provided'], 400);
        }

        $question = $content['question'];

        // Save the user's message in the database
        $userMessage = new ChatMessage(); // Replace `ChatMessage` with your entity
        $userMessage->setUserId(1); // Replace with dynamic user ID
        $userMessage->setSender('user');
        $userMessage->setMessage($question);
        $userMessage->setCreatedAt(new \DateTime());

        $entityManager->persist($userMessage);

        try {
            // Call the Flask API to get the chatbot's response
            $response = $this->httpClient->request(
                'POST',
                'http://localhost:5002/chat', // Your Flask API URL
                [
                    'json' => ['question' => $question],
                ]
            );

            $data = $response->toArray();

            // Save the chatbot's response in the database
            $chatbotMessage = new ChatMessage();
            $chatbotMessage->setUserId(1); // Replace with dynamic user ID
            $chatbotMessage->setSender('chatbot');
            $chatbotMessage->setMessage($data['response']);
            $chatbotMessage->setCreatedAt(new \DateTime());

            $entityManager->persist($chatbotMessage);
            $entityManager->flush();

            return new JsonResponse($data);
        } catch (\Exception $e) {
            return new JsonResponse(['error' => $e->getMessage()], 500);
        }
    }


    /**
     * @Route("/chatbot/history", name="chatbot_history", methods={"GET"})
     */
    public function getChatHistory(EntityManagerInterface $entityManager): JsonResponse
    {
        // Fetch messages for the current user (replace with dynamic user ID)
        $userId = 1; // Replace with dynamic user ID
        $messages = $entityManager->getRepository(ChatMessage::class)
            ->findBy(['userId' => $userId], ['createdAt' => 'ASC']);

        $history = [];
        foreach ($messages as $message) {
            $history[] = [
                'sender' => $message->getSender(),
                'message' => $message->getMessage(),
                'created_at' => $message->getCreatedAt()->format('Y-m-d H:i:s'),
            ];
        }

        return new JsonResponse($history);
    }
    /**
     * @Route("/chatbot/message/delete/{id}", name="chatbot_delete_message", methods={"DELETE"})
     */
    public function deleteMessage(int $id, EntityManagerInterface $entityManager): JsonResponse
    {
        $message = $entityManager->getRepository(ChatMessage::class)->find($id);

        if (!$message) {
            return new JsonResponse(['error' => 'Message not found'], 404);
        }

        try {
            $entityManager->remove($message);
            $entityManager->flush();

            return new JsonResponse(['success' => 'Message deleted']);
        } catch (\Exception $e) {
            return new JsonResponse(['error' => $e->getMessage()], 500);
        }
    }
    /**
     * @Route("/chatbot/conversation/delete/{userId}", name="chatbot_delete_conversation", methods={"DELETE"})
     */
    public function deleteConversation(int $userId, EntityManagerInterface $entityManager): JsonResponse
    {
        $messages = $entityManager->getRepository(ChatMessage::class)->findBy(['userId' => $userId]);

        if (!$messages) {
            return new JsonResponse(['error' => 'No conversation found'], 404);
        }

        try {
            foreach ($messages as $message) {
                $entityManager->remove($message);
            }

            $entityManager->flush();

            return new JsonResponse(['success' => 'Conversation deleted']);
        } catch (\Exception $e) {
            return new JsonResponse(['error' => $e->getMessage()], 500);
        }
    }


}
