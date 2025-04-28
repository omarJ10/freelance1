<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Process\Process;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Contracts\HttpClient\HttpClientInterface;

class PredictionInstagramController extends AbstractController
{
    private $httpClient;

    public function __construct(HttpClientInterface $httpClient)
    {
        $this->httpClient = $httpClient;
    }
    /**
     * @Route("/prediction/instagram", name="app_prediction_instagram", methods={"GET", "POST"})
     */
    public function app_prediction_instagram(Request $request): Response
    {
        $predictionValue = null;
        $videoDuration = null;
        $isSponsored = null;
        $day_of_week = null;
        $hour = null;
        $error = null;
        if ($request->isMethod('POST')) {
            $videoDuration = $request->get('videoDuration');
            $isSponsored = $request->get('isSponsored');
            $day_of_week = $request->get('day_of_week');
            $hour = $request->get('hour');

            if (is_null($videoDuration) || is_null($isSponsored) || is_null($day_of_week) || is_null($hour)) {
                return new JsonResponse([
                    'error' => 'Entrée invalide. Veuillez fournir toutes les données nécessaires.',
                ], 400);
            } else {
                try {
                    // Appeler l'API Flask
                    $response = $this->httpClient->request('POST', 'http://127.0.0.1:5000/predict/instagram', [
                        'json' => [
                            'videoDuration' => $videoDuration,
                            'isSponsored' => $isSponsored,
                            'day_of_week' => $day_of_week,
                            'hour' => $hour,
                        ],
                    ]);

                    $data = $response->toArray();

                    if (isset($data['error'])) {
                        $error = $data['error'];
                    } else {
                        $predictionValue = $data['predicted_category']; // Corrigez cette clé si Flask retourne autre chose
                        $this->addFlash('debug', 'Valeur prédite : ' . $predictionValue);
                    }
                } catch (\Exception $e) {
                    $error = "Erreur lors de la communication avec l'API Flask : " . $e->getMessage();
                }
            }
        }
        $user = $this->getUser();

        // Rendu de la page Twig
        return $this->render('prediction_instagram/index.html.twig', [
            'controller_name' => 'PredictionInstagramController',
            'error' => $error,
            'username' => $user->getUsername(),
            'best_prediction' => $predictionValue,
            'videoDuration' => $videoDuration,
            'isSponsored' => $isSponsored,
            'day_of_week' => $day_of_week,
            'hour' => $hour,
        ]);
    }
}
